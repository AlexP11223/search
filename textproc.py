from functools import lru_cache
import nltk
import nltk.corpus
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer


@lru_cache(maxsize=1)
def download_nltk_data_if_needed():
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')
    nltk.download('tagsets')
    nltk.download('stopwords')
    nltk.download('wordnet')


def get_stop_words(lang='english'):
    return set(nltk.corpus.stopwords.words(lang)).union(
        # looks like some punctuation symbols are not tagged correctly
        {'’', '–', '—', '−', '..', '“', '[', ']', '‘', "'", '…', '”', "''", '"', '•'})


def get_stop_tags():
    download_nltk_data_if_needed()
    return {'.',  # sentence terminator (., !, ?)
            ',',  # comma
            ':',  # colon or ellipsis (:, ;, ...)
            '--',  # dash
            '(', ')',  # parenthesis ((, ), [, ], {, })
            "'", '`',  # quotation
            }


def tokenize(text):
    download_nltk_data_if_needed()
    tokens = nltk.word_tokenize(text)
    return nltk.pos_tag(tokens)


def get_wordnet_pos(treebank_tag):
    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    else:
        return None


def lemmatize(tagged_words):
    wd_tagged_words = {(it[0], get_wordnet_pos(it[1])) for it in tagged_words}
    lemmatizer = WordNetLemmatizer()
    return [it[0] if it[1] is None else lemmatizer.lemmatize(it[0], it[1]) for it in wd_tagged_words]


def normalize_set(tagged_tokens, lemmatization=True):
    tagged_words = {(it[0].lower(), it[1]) for it in tagged_tokens if not it[1] in get_stop_tags()}
    if lemmatization:
        words = set(lemmatize(tagged_words))
    else:
        words = {it[0] for it in tagged_words}
    return words.difference(get_stop_words())


def normalize_list(tagged_tokens, lemmatization=True):
    tagged_words = [(it[0].lower(), it[1]) for it in tagged_tokens if not it[1] in get_stop_tags()]
    if lemmatization:
        words = lemmatize(tagged_words)
    else:
        words = [it[0] for it in tagged_words]
    stop_words = get_stop_words()
    words = [word for word in words if not word in stop_words]
    return words


def extract_terms_set(text, lemmatization=True):
    """
    Tokenizes text and returns normalized set of terms (no repetitions)
    """
    return normalize_set(tokenize(text), lemmatization)


def extract_terms_list(text, lemmatization=True):
    """
    Tokenizes text and returns normalized list of terms
    """
    return normalize_list(tokenize(text), lemmatization)
