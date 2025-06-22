import os
import json

# 파일을 읽어 dictionary 형태로 리턴
def read_json_file(filename, decode_new_line=False):
    json_data = open(filename, 'r', encoding='UTF-8').read()
    return json.loads(json_data)


def read_file(filename):
    return open(filename, 'r', encoding='UTF-8').read()

def read_fp(filename, mode ):
    return open( filename, mode, encoding='UTF-8')

def close_fp(fp):
    if fp:
        fp.close()

# 파일 Read and 검색 필터링
def read_file_and_search(filename, keyword):
    data = read_file(filename)
    if keyword.lower() in data.lower():
        return True

    return False


# data 저장
def write_file(filename, data):
    try:
        fp = open(filename, 'w', encoding='UTF-8')
        fp.write(data)
        fp.close()
        return True
    except Exception as e:
        print("ERROR = ", e)
        return False


def exist(path):
    return os.path.exists(path)


def delete_file(filename):
    if exist(filename):
        os.remove(filename)
        return True

    return False


# 파일 경로 조회
def get_file_path(full_path):
    path, file_name = os.path.split(full_path)
    return path, file_name


# 폴더 생성
def make_dir(dir):
    if not exist(dir):
        print("make dir = ", dir)
        os.makedirs(dir)
