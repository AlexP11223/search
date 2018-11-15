import pytest

from index import index
from search import Search
from utils import load_json

metadata_file_path = 'test_data/data.json'


@pytest.fixture(params=[{'lemmatization': False}, {'lemmatization': True}], ids=['no-lemm', 'lemm'])
def index_file(request, tmp_path):
    index_file = tmp_path / 'index.json'
    index(metadata_file_path, str(index_file), lemmatization=request.param['lemmatization'])
    return index_file


def test_index_basic(tmp_path):
    index_file = tmp_path / 'output' / 'index' / 'index.json'
    index(metadata_file_path, str(index_file), lemmatization=False)
    assert index_file.is_file()
    index_data = load_json(index_file)
    assert index_data['files']
    assert 3 == len(index_data['files'])
    assert index_data['terms']
    assert [0, 1, 2] == index_data['terms']['brutus']
    assert [0] == index_data['terms']['julius']
    assert [1] == index_data['terms']['fault']
    assert [0] == index_data['terms']['killed']


def test_index_lemmatized(tmp_path):
    index_file = tmp_path / 'output' / 'index' / 'index.json'
    index(metadata_file_path, str(index_file), lemmatization=True)
    assert index_file.is_file()
    index_data = load_json(index_file)
    assert index_data['files']
    assert 3 == len(index_data['files'])
    assert index_data['terms']
    assert [0, 1, 2] == index_data['terms']['brutus']
    assert [0] == index_data['terms']['julius']
    assert [1] == index_data['terms']['fault']
    assert [0] == index_data['terms']['kill']
    assert 'killed' not in index_data['terms']


def test_search(index_file):
    file1 = {'file': 'doc1.txt', 'url': 'example.com/doc1.pdf', 'title': "Doc 1"}
    file2 = {'file': 'doc2.txt', 'url': 'example.com/doc2.pdf', 'title': "Doc 2"}
    file3 = {'file': 'doc3.txt', 'url': 'example.com/doc3.pdf', 'title': "Doc 3"}

    search = Search(str(index_file))

    assert [] == search.find('Eyjafjallajokull')
    assert [] == search.find('')
    assert [] == search.find('          ')
    assert [file1, file2] == search.find('caesar')
    assert [file1, file2, file3] == search.find('brutus')
    assert [file1] == search.find('Brutus Julius')
    assert [file1] == search.find('Brutus,    jULiUS    ')
    assert [file1] == search.find('Brutus and Julius')
    assert [file1] == search.find('Julius killed')


@pytest.mark.parametrize("index_file", [{'lemmatization': True}], indirect=True)
def test_search_lemmatized(index_file):
    file1 = {'file': 'doc1.txt', 'url': 'example.com/doc1.pdf', 'title': "Doc 1"}
    file2 = {'file': 'doc2.txt', 'url': 'example.com/doc2.pdf', 'title': "Doc 2"}
    file3 = {'file': 'doc3.txt', 'url': 'example.com/doc3.pdf', 'title': "Doc 3"}

    search = Search(str(index_file))

    assert [file1] == search.find('Julius kill')
    assert [file1] == search.find('Julius KILLS')
    assert [file2] == search.find('nobles')
    assert [file3] == search.find('said')
