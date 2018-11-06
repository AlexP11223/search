Simple document search (boolean retrieval) created during an university course based on [Christopher D. Manning, Prabhakar Raghavan and Hinrich Schütze, Introduction to Information Retrieval, Cambridge University Press. 2008](https://nlp.stanford.edu/IR-book/).

Currently supports only AND queries, e.g. `machine learning optimization` to find documents containing all these words.

# Usage

Requirements:

- Python 3.7+
- [pipenv](https://pipenv.readthedocs.io/en/latest/)

Install dependencies by executing `pipenv install`. Use `pipenv shell` or `pipenv run` to run scripts.

Use PyTest to run tests: `python -m pytest -v test.py` or in PyCharm.

Run

```
python index.py data/data.json output/index.json
```

to create index file.

Run

```
python search.py output/index.json
```

to execute search queries.
