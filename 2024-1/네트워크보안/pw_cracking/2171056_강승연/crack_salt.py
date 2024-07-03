#import
import pandas as pd
import os
import hashlib
import string
import itertools

#txt 파일 파싱
cwd = os.getcwd()
filepath_hashed = os.path.join(cwd, '1MillionPassword_hashed.txt')
filepath_wordlist = os.path.join(cwd, '1MillionPassword_wordlist.txt')

df = pd.DataFrame(columns= ['hash', 'word'])

hashed_f = open(filepath_hashed)
wordlist_f = open(filepath_wordlist)
hash_list = []
word_list = []

for line in hashed_f.readlines():
  line = line.replace('\n', '')
  hash_list.append(line)

for line in wordlist_f.readlines():
  line = line.replace('\n', '')
  word_list.append(line)

#salt 찾기
chars = list(string.ascii_lowercase) + list(string.digits)
length = 4

salts = itertools.product(chars, repeat=length)
ans_salt = 0

for salt in salts:
  word_salt = word_list[0]+''.join(salt)
  print(word_salt+"에 대응하는 해시 찾는중")
  word_salt = word_salt.encode('utf-8')
  md5 = hashlib.md5()
  md5.update(word_salt)
  hash_salt = md5.hexdigest()
  if hash_list[0] == hash_salt:
    ans_salt = ''.join(salt)
    break

print(ans_salt)

#salt 저장
salt_file = "salt.txt"
with open(salt_file, "w") as file:
  file.write(str(ans_salt))