from functools import lru_cache
import nltk
import nltk.corpus


@lru_cache(maxsize=1)
def download_nltk_data_if_needed():
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')
    nltk.download('tagsets')
    nltk.download('stopwords')


def extract_terms(text):
    def tokenize():
        tokens = nltk.word_tokenize(text)
        return nltk.pos_tag(tokens)

    def normalize(tagged_tokens):
        stop_words = set(nltk.corpus.stopwords.words('english'))
        # looks like some punctuation symbols are not tagged correctly
        stop_words = stop_words.union({'’', '–', '—', '−', '..', '“', '[', ']', '‘', "'", '…', '”', "''", '"', '•'})
        stop_tags = {'.',  # sentence terminator (., !, ?)
                     ',',  # comma
                     ':',  # colon or ellipsis (:, ;, ...)
                     '--',  # dash
                     '(', ')',  # parenthesis ((, ), [, ], {, })
                     "'", '`',  # quotation
                     }
        words = {it[0].lower() for it in tagged_tokens if not it[1] in stop_tags}
        return words.difference(stop_words)

    download_nltk_data_if_needed()

    return normalize(tokenize())
