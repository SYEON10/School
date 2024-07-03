#import
import os
import hashlib

#저장된 salt 불러오기
cwd = os.getcwd()
salt_file = "salt.txt"

file = open(salt_file, 'r')
salt = file.read()
file.close()

#pw 파일 열기
filepath_wordlist = os.path.join(cwd, '1MillionPassword_wordlist.txt')
wordlist_f = open(filepath_wordlist)

#crack
idx = 1
for line in wordlist_f.readlines():
  pw = line.replace('\n', '')
  word_salt = pw+''.join(salt)
  pw_encode = word_salt.encode('utf-8')
  md5 = hashlib.md5()
  md5.update(pw_encode)
  hash = md5.hexdigest()
  print(str(idx)+'/'+'1000000 password has been cracked, hashed: '+hash+', cracked: '+str(pw))
  idx += 1