import argparse
import itertools
from sys import stdin

from sklearn.metrics import pairwise_distances

from textproc import extract_terms_set
from utils import load_json, filter_dict_keys
import jsonpickle


class Search:
    """
    Uses the specified index file for performing search queries
    """

    def __init__(self, index_file_path):
        index_data = load_json(index_file_path)
        config = index_data['config']
        mode = config.get('mode', 'bool')
        self.backend = {
            'bool': BooleanSearchBackend,
            'tfidf': TfIdfSearchBackend
        }[mode](index_data, config)

    def find(self, query_text):
        return self.backend.get_results(query_text)


class SearchBackend:
    def __init__(self, index_data, config):
        self.config = config
        self.index_data = index_data

    def _get_query_terms(self, query_text):
        return extract_terms_set(query_text.strip(), lemmatization=self.config['lemmatization'])

    def get_results(self, query_text):
        raise NotImplementedError('')


class BooleanSearchBackend(SearchBackend):
    def __init__(self, index_data, config):
        super().__init__(index_data, config)

    def get_results(self, query_text):
        query_terms = self._get_query_terms(query_text)
        if not query_terms:
            return []

        postings_lists = []
        for query_term in query_terms:
            if query_term not in self.index_data['terms']:
                return []
            postings_lists.append(set(self.index_data['terms'][query_term]))
        postings_lists.sort(key=lambda x: len(x), reverse=False)

        result_ids = sorted(list(set.intersection(*postings_lists)))
        return [filter_dict_keys(self.index_data['files'][i], allowed_keys={'file', 'title', 'url'})
                for i in result_ids]


class TfIdfSearchBackend(SearchBackend):
    def __init__(self, index_data, config):
        super().__init__(index_data, config)

        unpickler = jsonpickle.Unpickler()
        self.doc_term_matrix = unpickler.restore(index_data['tfidf_doc_term_matrix'])
        self.vectorizer = unpickler.restore(index_data['tfidf_vectorizer'])
        self.vectorizer.tokenizer = self._get_query_terms

    def get_results(self, query_text):
        if not self._get_query_terms(query_text):
            return []

        query_vector = self.vectorizer.transform([query_text])

        distances = pairwise_distances(self.doc_term_matrix, query_vector, metric='cosine').tolist()
        distances = list(zip(list(itertools.chain.from_iterable(distances)), self.index_data['files']))




def main():
    parser = argparse.ArgumentParser(
        description='''Reads data from the index file and accepts search queries from stdin
until empty line is entered.
Currently supports only AND queries
e.g. "machine learning optimization" to find documents containing all these words.''',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''Example:
  search.py output/index.json''')
    parser.add_argument('index_file', type=str, help='path to the index file')
    args = parser.parse_args()

    search = Search(args.index_file)

    while True:
        print('Enter search query: ')
        query = stdin.readline().strip()
        if not query:
            return
        results = search.find(query)
        if not results:
            print('Not found')
        else:
            print(f'Found {len(results)} documents:')
            for result in results:
                print(f'{result["title"]} ({result["file"]}, {result["url"]})')
        print()


if __name__ == '__main__':
    main()
