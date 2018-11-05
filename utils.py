import json
import os


def make_dirs_if_not_exist(path):
    os.makedirs(path, exist_ok=True)


def make_file_path_if_not_exists(file_path):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)


def load_json(file_path):
    with open(file_path, encoding='utf-8') as f:
        return json.load(f)


def write_json(data, file_path):
    make_file_path_if_not_exists(file_path)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def read_all_file_text(file_path, encoding='utf-8-sig'):
    with open(file_path, 'r', encoding=encoding) as f:
        return f.read()
