import json
import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


def get_newest(db):
    cur = db.cursor()
    cur.execute('SELECT id_str FROM newest_tweet WHERE id = 1')
    result = cur.fetchone()
    if result:
        return result[0]
    return None


def store_status(db, status, user_id):
    cur = db.cursor()
    cur.execute('''INSERT INTO tweet
    (id_str, created, author_name, author_screen_name, text, json, user_id)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''',
                (status.id,
                 status.created_at,
                 status.author.name,
                 status.author.screen_name,
                 status.text,
                 json.dumps(status._json),
                 user_id
                ))
    db.commit()


def update_newest(db, user_id, newest_id):
    cur = db.cursor()
    if newest_id:
        cur.execute(
            'REPLACE INTO newest_tweet (id, user_id, id_str) values (?, ?, ?)',
            (1, user_id, newest_id))
    db.commit()
