import pytest

from index import BooleanIndex
from search import Search
from utils import load_json

metadata_file_path = 'test_data/data.json'


@pytest.fixture(params=[{'lemmatization': False}, {'lemmatization': True}], ids=['no-lemm', 'lemm'])
def index_file(request, tmp_path):
    index_file = tmp_path / 'index.json'
    BooleanIndex(metadata_file_path, lemmatization=request.param['lemmatization']).create(str(index_file))
    return index_file


@pytest.fixture
def docs():
    return [{'file': 'doc1.txt', 'url': 'example.com/doc1.pdf', 'title': "Doc 1"},
            {'file': 'doc2.txt', 'url': 'example.com/doc2.pdf', 'title': "Doc 2"},
            {'file': 'doc3.txt', 'url': 'example.com/doc3.pdf', 'title': "Doc 3"}]


def test_index_basic(tmp_path):
    index_file = tmp_path / 'output' / 'index' / 'index.json'
    BooleanIndex(metadata_file_path, lemmatization=False).create(str(index_file))
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
    BooleanIndex(metadata_file_path, lemmatization=True).create(str(index_file))
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


def test_search(index_file, docs):
    search = Search(str(index_file))
    assert [] == search.find('Eyjafjallajokull')
    assert [] == search.find('')
    assert [] == search.find('          ')
    assert [docs[0], docs[1]] == search.find('caesar')
    assert [docs[0], docs[1], docs[2]] == search.find('brutus')
    assert [docs[0]] == search.find('Brutus Julius')
    assert [docs[0]] == search.find('Brutus,    jULiUS    ')
    assert [docs[0]] == search.find('Brutus and Julius')
    assert [docs[0]] == search.find('Julius killed')


@pytest.mark.parametrize("index_file", [{'lemmatization': True}], indirect=True)
def test_search_lemmatized(index_file, docs):
    search = Search(str(index_file))
    assert [docs[0]] == search.find('Julius kill')
    assert [docs[0]] == search.find('Julius KILLS')
    assert [docs[1]] == search.find('nobles')
    assert [docs[2]] == search.find('said')
