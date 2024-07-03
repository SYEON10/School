import hashlib

# 덤프된 파일 경로
dump_file_path = './1928_procdump.bin'
# 해시 값을 저장할 파일 경로
hash_file_path = './1928_procdump_sha256.txt'

# SHA-256 해시 계산 함수
def calculate_sha256(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for byte_block in iter(lambda: f.read(4096), b''):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

# 해시 값 계산
hash_value = calculate_sha256(dump_file_path)

# 해시 값을 파일에 저장
with open(hash_file_path, 'w') as hash_file:
    hash_file.write(f'SHA-256: {hash_value}\n')

print(f'SHA-256 hash value saved to {hash_file_path}')
