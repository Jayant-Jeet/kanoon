import csv
import os
import sys
import itertools

from jina.flow import Flow
from jina.proto import jina_pb2


def config():
    parallel = 2 if sys.argv[1] == 'index' else 1

    os.environ.setdefault('JINA_MAX_DOCS', '100')
    os.environ.setdefault('JINA_PARALLEL', str(parallel))
    os.environ.setdefault('JINA_SHARDS', str(4))
    os.environ.setdefault('JINA_WORKSPACE', './workspace')
    os.makedirs(os.environ['JINA_WORKSPACE'], exist_ok=True)
    os.environ.setdefault('JINA_PORT', str(65481))


def input_fn():
    lyrics_file = os.environ.setdefault('JINA_DATA_PATH', 'data.csv')
    with open(lyrics_file, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in itertools.islice(reader, int(os.environ['JINA_MAX_DOCS'])):
            d = jina_pb2.Document()
            d.tags['Section'] = row[0]
            d.text = row[1]
            yield d


# for index
def index():
    f = Flow.load_config('flows/index.yml')

    with f:
        f.index(input_fn, batch_size=8)

    # for search


def search():
    f = Flow.load_config('flows/query.yml')

    with f:
        f.block()


# for test before put into docker
def dryrun():
    f = Flow.load_config('flows/query.yml')

    with f:
        pass


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('choose between "index/search/dryrun" mode')
        exit(1)
    if sys.argv[1] == 'index':
        config()
        index()
    elif sys.argv[1] == 'search':
        config()
        search()
    elif sys.argv[1] == 'dryrun':
        config()
        dryrun()
    else:
        raise NotImplementedError(f'unsupported mode {sys.argv[1]}')
