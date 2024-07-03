import os
import query
import pandas as pd

# 정상작동 확인 및 성공 메시지 출력
def check_complete(result, msg):
    if len(result) == 0:
        print(msg)
        return True
    return False

# Error 여부 확인 및 오류 메시지 출력
def check_error(result, error, msg):
    if result.find(error) != -1 :
        print(msg)

def check_int(result, msg):
    if not result.isdigit() : 
        print(msg)
        return True
    return False

#1. initialize database
def create_table(repo):
    repo.execute_sql(query.sql_create_table, commit = False)

# table들을 create하고 csv 파일로 초기화함
def init_db(repo, file_path):
    create_table(repo)

    init_db = pd.read_csv(file_path)

    movie = init_db.iloc[:,0:3]
    movie.drop_duplicates(keep='first', inplace=True)
    audience = init_db.iloc[:,3:5]
    audience.drop_duplicates(keep='first', inplace=True)

    repo.init_with_csv('movie(title, director, price)', movie)
    repo.init_with_csv('audience(name, age)', audience)

    for index, row in init_db.iterrows():
        mov_result = repo.execute_sql(query.sql_get_mov_id(str(row.iloc[0])))
        aud_result = repo.execute_sql(query.sql_get_aud_id(str(row.iloc[3]), str(row.iloc[4])))
        if len(mov_result) == 0 or len(aud_result) == 0:
            continue
        mov_id = int(repo.execute_sql(query.sql_get_mov_id(str(row.iloc[0])))[0][0])
        aud_id = int(repo.execute_sql(query.sql_get_aud_id(str(row.iloc[3]), str(row.iloc[4])))[0][0])
        repo.execute_sql(query.sql_insert_reservation(mov_id, aud_id))

    print("Database successfully initialized")

#2. print all movies
def print_all_movies(repo):
    result = repo.execute_sql(query.sql_select_movie)
    query.print_table(result, query.header_type.movie)

#3. print all users
def print_all_users(repo):
    result = repo.execute_sql(query.sql_select_audience)
    query.print_table(result, query.header_type.audience)

#4. insert a new movie
def insert_movie_input(repo) :
    title = input("Movie title: ")
    director = input("Movie director: ")
    price = input("Movie price: ")
    if check_int(price, "price must be integer") : return
    insert_movie(repo, title, director, price)

def insert_movie(repo, title, director, price):
    result = repo.execute_sql(query.sql_insert_movie(title, director, price))
    if check_complete(result, 'One movie successfully inserted') : return
    check_error(result, 'unique_title', f'Movie {title} already exists')
    check_error(result, 'price_range', 'Movie price should be from 0 to 100000')

#5. insert a new user
def insert_user_input(repo) :
    name = input("User name: ")
    age = input("User age: ")
    if check_int(age, "age must be integer") : return
    insert_user(repo, name, age)

def insert_user(repo, name, age):
    result = repo.execute_sql(query.sql_insert_audience(name, age))
    if check_complete(result, 'One user successfully inserted') : return
    check_error(result, 'age_range', 'User age should be from 12 to 110')
    check_error(result, 'unique_name_age', f'User ({name}, {age}) already exists')

#6. remove a movie
def remove_movie_input(repo):
    mov_id = input("Moive id: ")
    if check_int(mov_id, "Movie id must be integer") : return
    remove_movie(repo, mov_id)

def remove_movie(repo, mov_id):
    #사전에 존재하는지 check
    check = repo.execute_sql(query.sql_id_check('movie', mov_id))
    if check_complete(check, f'Movie {mov_id} does not exist'): return
    result = repo.execute_sql(query.sql_delete("movie", mov_id))
    check_complete(result, 'One movie successfully removed')

#7. remove a user
def remove_user_input(repo):
    aud_id = input("User ID: ")
    if check_int(aud_id, "User id must be integer") : return
    remove_user(repo, aud_id)

def remove_user(repo, aud_id):
    #사전에 존재하는지 check
    check = repo.execute_sql(query.sql_id_check('audience', aud_id))
    if check_complete(check, f'User {aud_id} does not exist') : return
    result = repo.execute_sql(query.sql_delete("audience", aud_id))
    check_complete(result, 'One user successfully removed')

#8. book a movie
def book_movie_input(repo):
    mov_id = input("Movie ID: ")
    if check_int(mov_id, "Movie id must be integer") : return
    aud_id = input("User ID: ")
    if check_int(aud_id, "User id must be integer") : return
    book_movie(repo, mov_id, aud_id)

def book_movie(repo, mov_id, aud_id):
    check = repo.execute_sql(query.sql_check_reservation_full(mov_id))
    if (int(check[0][0]) >= 10) : 
        print(f'Movie {mov_id} has already been fully booked')
        return
    result = repo.execute_sql(query.sql_insert_reservation(mov_id, aud_id))
    if check_complete(result, 'Movie successfully booked') : return
    check_error(result, 'PRIMARY', f'User {aud_id} has already booked movie {mov_id}')
    check_error(result, 'fk_mov', f'Movie {mov_id} does not exist')
    check_error(result, 'fk_aud', f'User {aud_id} does not exist')

#9. rate a movie
def rate_movie_input(repo):
    mov_id = input("Movie ID: ")
    if check_int(mov_id, "Movie id must be integer") : return
    aud_id = input("User ID: ")
    if check_int(aud_id, "User id must be integer") : return
    grade = input("Ratings (1~5): ")
    if check_int(grade, "Rate must be integer") : return
    rate_movie(repo, mov_id, aud_id, grade)

def rate_movie(repo, mov_id, aud_id, grade):
    check = repo.execute_sql(query.sql_check_reservation(mov_id, aud_id))
    if (len(check) == 0) : 
        print(f'User {aud_id} has not booked movie {mov_id} yet')
        return
    if (str(check[0][0]).isdigit()) and (1<=int(check[0][0])<=5) :
        print(f'User {aud_id} has already rated movie {mov_id}')
        return
    result = repo.execute_sql(query.sql_update_reservation(mov_id, aud_id, grade))
    if check_complete(result, 'Movie successfully rated') : return
    check_error(result, 'fk_mov', f'Movie {mov_id} does not exist')
    check_error(result, 'fk_aud', f'User {aud_id} does not exist')
    check_error(result, 'grade_range', 'rate should be from 1 to 5')

#10. print all users who booked for a movie
def print_book_movie_input(repo):
    mov_id = input("Movie ID: ")
    if check_int(mov_id, "Movie id must be integer") : return
    print_book_movie(repo, mov_id)

def print_book_movie(repo, mov_id):
    result = repo.execute_sql(query.sql_select_reservation_by_movie(mov_id))
    if len(result) == 0:
        print(f'Movie {mov_id} does not exist')
        return
    query.print_table(result, query.header_type.reserve_aud)

#11. print all movies booked by a user
def print_book_user_input(repo):
    aud_id = input("User ID: ")
    if check_int(aud_id, "User id must be integer") : return
    print_book_user(repo, aud_id)

def print_book_user(repo, aud_id):
    result = repo.execute_sql(query.sql_select_reservation_by_audience(aud_id))
    if len(result) == 0:
        print(f'User {aud_id} does not exist')
        return
    query.print_table(result, query.header_type.reserve_mov)

#13. reset database
def reset_input(repo):
    allow = input("Are you really gonna reset this database? (y/n): ")
    if allow == 'y':
        reset(repo)

def reset(repo):
    check = repo.execute_sql(query.sql_show_tables)
    if len(check) != 0 :
        repo.execute_sql(query.sql_drop_db, commit=False)
        
    init_db(repo, file_path)

actions = """============================================================
1. initialize database
2. print all movies
3. print all users
4. insert a new movie
5. insert a new user
6. remove a movie
7. remove a user
8. book a movie
9. rate a movie
10. print all users who booked for a movie
11. print all movies booked by a user
12. exit
13. reset database
============================================================"""

pwd = os.getcwd()
file_path = pwd+'/data.csv'

def main():
    repo = query.Repository()

    while True :
        print(actions)
        action = int(input('Select your action: '))
        if action == 1 : init_db(repo, file_path) # 1. initialize database
        elif action == 2 : print_all_movies(repo) # 2. print all movies
        elif action == 3 : print_all_users(repo) # 3. print all users
        elif action == 4 : insert_movie_input(repo) # 4. insert a new movie
        elif action == 5 : insert_user_input(repo) # 5. insert a new user
        elif action == 6 : remove_movie_input(repo) # 6. remove a movie
        elif action == 7 : remove_user_input(repo) # 7. remove a user
        elif action == 8 : book_movie_input(repo) # 8. book a movie
        elif action == 9 : rate_movie_input(repo) # 9. rate a movie
        elif action == 10 : print_book_movie_input(repo) # 10. print all users who booked for a movie
        elif action == 11 : print_book_user_input(repo) # 11. print all movies booked by a user
        elif action == 12 : print("Bye!"); break # 12. exit
        elif action == 13 : reset_input(repo) # 13. reset database
        else : print("Invalid action")
        
    repo.close_connection()

if __name__ == "__main__":
    main()