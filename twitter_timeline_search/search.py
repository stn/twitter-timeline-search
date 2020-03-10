import os
import shutil
import unicodedata

import click
from flask import current_app, g
from flask.cli import with_appcontext

from whoosh.index import create_in, open_dir
from whoosh.fields import Schema, KEYWORD, STORED
from whoosh.qparser import QueryParser

import MeCab


def get_search():
    if 'search' not in g:
        g.search = open_dir(current_app.config['SEARCH'])

    return g.search


def close_search(e=None):
    pass


def init_search():
    schema = Schema(text=KEYWORD, id=STORED)
    search_dir = current_app.config['SEARCH']
    if os.path.exists(search_dir):
        shutil.rmtree(search_dir)
    os.mkdir(search_dir)
    create_in(search_dir, schema)


@click.command('init-search')
@with_appcontext
def init_search_command():
    """Clear the existing index and create new search index."""
    init_search()
    click.echo('Initialized the search index.')


def init_app(app):
    app.teardown_appcontext(close_search)
    app.cli.add_command(init_search_command)


def tokenize(text):
    text = unicodedata.normalize('NFKC', text)
    mecab = MeCab.Tagger('-Owakati')
    return unicodedata.normalize('NFKC', mecab.parse(text))


def add_tweet(writer, status):
    writer.add_document(text=tokenize(status.text), id=status.id_str)


def search_tweets(query, limit=20):
    ix = get_search()
    with ix.searcher() as searcher:
        parser = QueryParser("text", ix.schema)
        q = parser.parse(tokenize(query))
        results = searcher.search(q, limit=limit)
        return [r['id'] for r in results]
