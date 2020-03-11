import json
import os
import tweepy

import click
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from flask.cli import with_appcontext
from werkzeug.exceptions import abort

from twitter_timeline_search.auth import login_required
from twitter_timeline_search.db import get_db, get_newest, store_status, update_newest
from twitter_timeline_search.search import get_search, add_tweet, search_tweets


bp = Blueprint('tweet', __name__)


def template_data(row):
    js = json.loads(row['json'])
    status = {}
    status['user_name'] = js['user']['name']
    status['user_screen_name'] = js['user']['screen_name']
    status['text'] = js['text']
    status['created'] = row['created']
    status['profile_image'] = js['user']['profile_image_url_https'].replace('_normal', '_reasonably_small')
    return status


@bp.route('/')
@login_required
def index():
    db = get_db()
    rows = db.execute('SELECT created, json FROM tweet WHERE user_id = ? ORDER BY created DESC LIMIT 20',
                          (g.user['id'],)).fetchall()
    statuses = [template_data(row) for row in rows]
    return render_template('tweet/index.html', statuses=statuses)


def process_sync(user_id,
         twitter_consumer_key, twitter_consumer_secret,
         twitter_access_token, twitter_access_token_secret):
    auth = tweepy.OAuthHandler(twitter_consumer_key, twitter_consumer_secret)
    auth.set_access_token(twitter_access_token, twitter_access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True)

    db = get_db()
    ix = get_search()
    writer = ix.writer()
    since_id = get_newest(db)
    newest_id = None
    # https://developer.twitter.com/en/docs/tweets/timelines/api-reference/get-statuses-home_timeline
    for status in tweepy.Cursor(api.home_timeline,
                                since_id=since_id,
                                count=200).items():
        print(status.id_str)
        store_status(db, status, user_id)
        add_tweet(writer, status)
        if newest_id is None:
            newest_id = status.id_str
    writer.commit()
    update_newest(db, user_id, newest_id)
    print(api.rate_limit_status()['resources']['statuses']['/statuses/home_timeline'])


@bp.route('/sync')
@login_required
def sync():
    process_sync(g.user['id'],
         g.user['twitter_consumer_key'], g.user['twitter_consumer_secret'],
         g.user['twitter_access_token'], g.user['twitter_access_token_secret'])
    return redirect(url_for('index'))


@click.command('sync')
@click.argument('user')
@with_appcontext
def sync_command(user):
    """Sync tweets for the given user."""
    if not user:
        return

    row = get_db().execute(
        'SELECT id, username, twitter_consumer_key, twitter_consumer_secret, twitter_access_token, twitter_access_token_secret FROM user WHERE username = ?', (user,)
    ).fetchone()
    if not row:
        click.echo('user unknown')
        return

    process_sync(row['id'],
                 row['twitter_consumer_key'], row['twitter_consumer_secret'],
                 row['twitter_access_token'], row['twitter_access_token_secret'])
    click.echo('Synced user\'s tweets')


@bp.route('/search')
@login_required
def search():
    query = request.args.get('q', '')
    statuses = []
    if query:
        results = search_tweets(query)
        db = get_db()
        rows = db.execute('''
            SELECT * FROM tweet
            WHERE user_id = ? AND id_str IN ({})
            ORDER BY created DESC
            '''.format(','.join(results)), (g.user['id'],)).fetchall()
        statuses = [template_data(row) for row in rows]
    return render_template('tweet/index.html', statuses=statuses, q=query)


def init_app(app):
    app.cli.add_command(sync_command)

