from index import index
from utils import load_json

metadata_file_path = 'test_data/data.json'


def test_index(tmp_path):
    index_file = tmp_path / 'output' / 'index' / 'index.json'
    index(metadata_file_path, str(index_file))
    assert index_file.is_file()
    index_data = load_json(index_file)
    assert index_data['files']
    assert 3 == len(index_data['files'])
    assert index_data['terms']
    assert [0, 1, 2] == index_data['terms']['brutus']
    assert [0] == index_data['terms']['julius']
    assert [1] == index_data['terms']['fault']
