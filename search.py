import argparse
from sys import stdin
from textproc import extract_terms
from utils import load_json, filter_dict_keys


class Search:
    """
    Uses the specified index file for performing search queries
    """

    def __init__(self, index_file_path):
        self.index_data = load_json(index_file_path)

    def find(self, query_text):
        query_terms = extract_terms(query_text.strip())
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
