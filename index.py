"""
Indexes the files specified in the metadata json file (e.g. data/data.json) and creates index file
"""
from functools import lru_cache

import nltk
import sys
from pathlib import Path
from utils import load_json, write_json, read_all_file_text


@lru_cache(maxsize=1)
def download_nltk_data_if_needed():
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')
    nltk.download('tagsets')


def tokenize(text):
    download_nltk_data_if_needed()

    tokens = nltk.word_tokenize(text)
    tagged_tokens = nltk.pos_tag(tokens)

    return tagged_tokens


def extract_terms(tagged_tokens):
    stop_words = {'a', 'an', 'the', 'is', 'are', 'at', 'which', 'that', 'on', 'to'}
    stop_tags = {'.',  # sentence terminator (., !, ?)
                 ',',  # comma
                 ':',  # colon or ellipsis (:, ;, ...)
                 '--',  # dash
                 '(', ')',  # parenthesis ((, ), [, ], {, })
                 "'", '`',  # quotation
                 }
    words = {it[0].lower() for it in tagged_tokens if not it[1] in stop_tags}
    words = words.difference(stop_words)

    return words


def load_terms(file_path):
    print('Loading terms from ' + str(file_path))

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
    metadata = load_json(metadata_file_path)
    files = [{'id': i, 'file': it['file'], 'title': it['title']} for i, it in enumerate(metadata)]
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
