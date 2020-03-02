import argparse
from datetime import datetime
from pathlib import Path
from textproc import extract_terms_set, extract_terms_list
from utils import load_json, write_json, read_all_file_text
from sklearn.feature_extraction.text import TfidfVectorizer
import jsonpickle


class Index:
    """
    Indexes the files specified in the metadata json file (e.g. data/data.json) and creates index file
    """

    def __init__(self, metadata_file_path, lemmatization=True):
        self._lemmatization = lemmatization

        metadata = load_json(metadata_file_path)
        self._input_dir = Path(metadata_file_path).parent
        self._files = [{'id': i,
                        'file': it['file'],
                        'title': it['title'],
                        'url': it['url']
                        } for i, it in enumerate(metadata)]

    def _make_config(self):
        return {'lemmatization': self._lemmatization}

    def _index(self):
        """
        Produces index data, must be implemented in subclasses
        :return: dict
        """
        raise NotImplementedError('')

    def create(self, index_file_path):
        data = {'config': self._make_config(), **self._index()}
        write_json(data, index_file_path)


class BooleanIndex(Index):
    def __init__(self, metadata_file_path, lemmatization=True):
        super().__init__(metadata_file_path, lemmatization)

    @staticmethod
    def _merge_terms(terms, new_terms):
        for term in new_terms:
            if term in terms:
                terms[term] += new_terms[term]
            else:
                terms[term] = new_terms[term]
        return terms

    def _load_terms(self, file_path):
        print(f'[{datetime.now().strftime("%H:%M:%S.%f")[:-3]}] Loading terms from {file_path}')

        text = read_all_file_text(file_path)

        return extract_terms_set(text, lemmatization=self._lemmatization)

    def _index(self):
        terms = {}
        for file in self._files:
            file_terms = self._load_terms(self._input_dir / file['file'])
            file_terms = {term: [file['id']] for term in file_terms}
            terms = self._merge_terms(terms, file_terms)
        return {'files': self._files, 'terms': terms}


class TfIdfIndex(Index):
    def __init__(self, metadata_file_path, lemmatization=True):
        super().__init__(metadata_file_path, lemmatization)

    def _make_config(self):
        return {**super()._make_config(), 'mode': 'tfidf'}

    def _index(self):
        vectorizer = TfidfVectorizer(tokenizer=lambda text: extract_terms_list(text, self._lemmatization))
        doc_term_matrix = vectorizer.fit_transform([read_all_file_text(self._input_dir / file['file']) for file in self._files])

        print(f'Created {doc_term_matrix.shape} doc-term matrix')

        # It is possible save only some vectorizer properties (like vocabulary, idf) instead of pickling the whole object
        # but there is no way to do this with TfidfVectorizer except messing with private properties
        # as shown here http://thiagomarzagao.com/2015/12/08/saving-TfidfVectorizer-without-pickles/
        # which is probably not a good idea, can break in future sklearn versions, etc.
        # The doc-term matrix is also serialized in not a very human-readable format unfortunately,
        # it is possible to store it in a less efficient but simpler format via .toarray().tolist()
        pickler = jsonpickle.Pickler()
        return {'files': self._files, 'tfidf_doc_term_matrix': pickler.flatten(doc_term_matrix), 'tfidf_vectorizer': pickler.flatten(vectorizer)}


def main():
    parser = argparse.ArgumentParser(
        description='''Indexes the files specified in the metadata json file (e.g. data/data.json)
and creates index file''',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''Example:
  index.py data/data.json output/index.json''')
    parser.add_argument('metadata_file', type=str, help='path to the metadata json file')
    parser.add_argument('output_index_file', type=str, help='path to the index file (that will be created)')
    parser.add_argument('--disable-lemmatizer', action='store_true', help='if specified, lemmatization is not performed')
    parser.add_argument('--mode', choices={'bool', 'tfidf'}, default='bool', help='index/search type: boolean retrieval or TF-IDF (default boolean)')
    args = parser.parse_args()

    {
        'bool': lambda _: BooleanIndex(args.metadata_file, lemmatization=not args.disable_lemmatizer).create(args.output_index_file),
        'tfidf': lambda _: TfIdfIndex(args.metadata_file, lemmatization=not args.disable_lemmatizer).create(args.output_index_file)
    }[args.mode](None)


if __name__ == '__main__':
    main()
