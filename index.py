from datetime import datetime
import sys
from pathlib import Path
from textproc import tokenize, extract_terms
from utils import load_json, write_json, read_all_file_text


def load_terms(file_path):
    print(f'[{datetime.now().strftime("%H:%M:%S.%f")[:-3]}] Loading terms from {file_path}')

    text = read_all_file_text(file_path)

    return extract_terms(tokenize(text))


def merge_terms(terms, new_terms):
    for term in new_terms:
        if term in terms:
            terms[term] += new_terms[term]
        else:
            terms[term] = new_terms[term]
    return terms


def index(metadata_file_path, index_file_path):
    """
    Indexes the files specified in the metadata json file (e.g. data/data.json) and creates index file
    """
    metadata = load_json(metadata_file_path)
    files = [{'id': i, 'file': it['file'], 'title': it['title'], 'url': it['url']} for i, it in enumerate(metadata)]
    input_dir = Path(metadata_file_path).parent
    terms = {}
    for file in files:
        file_terms = load_terms(input_dir / file['file'])
        file_terms = {term: [file['id']] for term in file_terms}
        terms = merge_terms(terms, file_terms)
    data = {'files': files, 'terms': terms}
    write_json(data, index_file_path)


def show_usage():
    print('Usage:')
    print('    python index.py metadata_file output_index_file')
    print('Example:')
    print('    python index.py data/data.json output/index.json')


def main():
    if len(sys.argv) < 3:
        show_usage()
        return

    metadata_file_path = sys.argv[1]
    index_file_path = sys.argv[2]

    index(metadata_file_path, index_file_path)


if __name__ == '__main__':
    main()
