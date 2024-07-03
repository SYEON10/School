from mysql.connector import connect, Error
from enum import Enum
import pandas as pd

# 실제 데이터베이스와의 모든 통신을 담당한다. (연결/SQL Query)
class Repository:
    # 데이터베이스와의 연결 생성
    def __init__(self):
        db_name ='movie_reserving'
        self.connection = connect(
            host ='127.0.0.1',
            user ='DB',
            password ='0309',
            db =db_name,
            charset ='utf8'
        )
        if not self.connection.is_connected() :
            print("[ERROR]MySQL Server와의 연결에 문제가 있습니다. ")
            exit()

    # sql문을 실행시키고 결과와 에러를 반환한다.
    def execute_sql(self, sql, commit = True):
        if not self.connection.is_connected():
            self.__init__()

        cursor = self.connection.cursor()
        
        try :
            cursor.execute(sql)
            result = cursor.fetchall()
            if commit == True :
                self.connection.commit()
            return result
        except Error as e:
            self.connection.rollback()
            return e.msg
        finally:
            cursor.close()
        
    # data frame 을 input으로, 해당 data frame을 DB에 Insert한다.
    def init_with_csv(self, table_header, df):
        data = ""
        for x in df.to_records(index=False) :
            t = str(tuple(x))
            data += ',' + t
        data = data[1:]
        sql = f"INSERT INTO {table_header} VALUES {data};"
        self.execute_sql(sql)
            
    # connection을 종료한다.
    def close_connection(self):
        self.connection.close()

# 형식에 맞게 출력한다.
def print_table(data, header_query):
    header_info = header[header_query.value]
    seperator = '-' * sum(header_info["format"])
    format = "".join([f"{{:<{w}}}" for w in header_info["format"]])
    print(seperator)
    header_line = format.format(*header_info["element"])
    print(header_line)
    print(seperator)
    for row in data:
        row_line = format.format(*[str(item) for item in row])
        print(row_line)
    print(seperator)

# print_table 출력 시 사용되는 헤더 목록이다.
header_format_movie = [5, 80, 35, 10, 5, 5]
header_format_audience = [10, 30, 5]
header_format_reserve_aud = [10, 30, 5, 5]
header_format_reserve_mov = [10, 80, 35, 5]
header_select_movie = ["id", "title", "director", "price", "reservation", "avg. rating"]
# 중략
header_select_audience= ["id", "name", "age"]
header_select_reservation_by_audience= ["id", "name", "age", "rating"]
header_select_reservation_by_movie= ["id", "title", "director", "rating"]

# 헤더를 Dictionary 로 만들어 Enum으로 접근하기 쉽게 만든다.
header = {
    1 : {"format": header_format_movie, "element": header_select_movie},
    2 : {"format": header_format_audience, "element": header_select_audience},
    3 : {"format": header_format_reserve_aud, "element": header_select_reservation_by_audience},
    4 : {"format": header_format_reserve_mov, "element": header_select_reservation_by_movie}
}

# Enum으로 Header를 접근할 수 있게 하여 오접근을 막는다.
class header_type(Enum):
    movie = 1
    audience = 2
    reserve_aud = 3
    reserve_mov = 4

### Input 없는 SQL문###

sql_drop_db = """DROP TABLE reservation;
DROP TABLE movie;
DROP TABLE audience;
"""

sql_select_movie="""SELECT movie.*, COUNT(*) AS 'reservation', AVG(grade) AS 'avg. rating'
FROM movie LEFT JOIN reservation ON movie.id = mov_id
GROUP BY id
ORDER BY id;"""

sql_select_audience="""SELECT *
FROM audience
ORDER BY id;"""

sql_show_tables = """SHOW TABLES;"""

sql_create_table = """CREATE TABLE movie (
  id INTEGER AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(80) NOT NULL,
  director VARCHAR(35) NOT NULL,
  price INTEGER NOT NULL,
  CONSTRAINT unique_title UNIQUE (title),
  CONSTRAINT price_range CHECK (price BETWEEN 0 AND 100000)
);

CREATE TABLE audience (
  id INTEGER AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(30) NOT NULL,
  age INTEGER NOT NULL,
  CONSTRAINT age_range CHECK (age BETWEEN 12 AND 110),
  CONSTRAINT unique_name_age UNIQUE (name, age)
);

CREATE TABLE reservation (
  mov_id INTEGER,
  aud_id INTEGER,
  grade INTEGER,
  PRIMARY KEY (mov_id, aud_id),
  CONSTRAINT grade_range CHECK (grade BETWEEN 1 AND 5),
  CONSTRAINT fk_mov FOREIGN KEY (mov_id) REFERENCES movie(id) ON DELETE CASCADE,
  CONSTRAINT fk_aud FOREIGN KEY (aud_id) REFERENCES audience(id) ON DELETE CASCADE
);"""

### Input 있는 SQL문###
def sql_insert_movie(title, director, price):
    return f"INSERT INTO movie(title, director, price) VALUES ('{title}', '{director}', {price});"

def sql_insert_audience(name, age):
    return f"INSERT INTO audience(name, age) VALUES ('{name}', {age});"

def sql_check_reservation_full(mov_id):
    return f"SELECT COUNT(*) FROM reservation WHERE mov_id = {mov_id};"

def sql_check_reservation(mov_id, aud_id):
    return f"SELECT grade FROM reservation WHERE mov_id = {mov_id} and aud_id = {aud_id}"

def sql_insert_reservation(mov_id, aud_id):
    return f"INSERT INTO reservation(mov_id, aud_id) VALUES ({mov_id}, {aud_id});"

def sql_update_reservation(mov_id, aud_id, grade):
    return f"""UPDATE reservation
SET grade = {grade}
WHERE mov_id = {mov_id} and aud_id = {aud_id};
"""

def sql_id_check(table, id):
    return f"SELECT * FROM {table} WHERE id = {id}"

def sql_select_reservation_by_movie(mov_id) :
    return f"""SELECT audience.*, grade
FROM audience LEFT JOIN reservation ON audience.id = reservation.aud_id
WHERE mov_id = {mov_id}
ORDER BY id;"""

def sql_select_reservation_by_audience(aud_id):
    return f"""SELECT id, title, director, grade
FROM movie LEFT JOIN reservation ON movie.id = reservation.mov_id
WHERE aud_id = {aud_id}
ORDER BY id;"""

def sql_delete(table, mov_id):
    return f"DELETE FROM {table} WHERE id = {mov_id};"

def sql_get_mov_id(title):
    return f'SELECT id FROM movie WHERE title = "{title}"'

def sql_get_aud_id(name, age):
    return f'SELECT id FROM audience WHERE name = "{name}" AND age = {age}'