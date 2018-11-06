import sys
from sys import stdin
from textproc import tokenize, extract_terms
from utils import load_json, filter_dict_keys


class Search:
    """
    Uses the specified index file for performing search queries
    """

    def __init__(self, index_file_path):
        self.index_data = load_json(index_file_path)

    def find(self, query_text):
        query_terms = extract_terms(tokenize(query_text.strip()))
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


def show_usage():
    print('Reads data from the index file and accepts search queries from stdin')
    print('until empty line is entered.')
    print('Currently supports only AND queries')
    print('e.g. "machine learning optimization" to find documents containing all these words.')
    print('Usage:')
    print('    python search.py index_file')
    print('Example:')
    print('    python search.py output/index.json')


def main():
    if len(sys.argv) < 2:
        show_usage()
        return

    index_file_path = sys.argv[1]

    search = Search(index_file_path)

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
