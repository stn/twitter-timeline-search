import json
import os
import tweepy

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
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


@bp.route('/sync')
@login_required
def sync():
    auth = tweepy.OAuthHandler(g.user['twitter_consumer_key'],
                               g.user['twitter_consumer_secret'])
    auth.set_access_token(g.user['twitter_access_token'],
                          g.user['twitter_access_token_secret'])
    api = tweepy.API(auth, wait_on_rate_limit=True)

    db = get_db()
    ix = get_search()
    writer = ix.writer()
    since_id = get_newest(db)
    newest_id = None
    for status in tweepy.Cursor(api.home_timeline, since_id=since_id).items(20):
        store_status(db, status, g.user['id'])
        add_tweet(writer, status)
        if newest_id is None:
            newest_id = status.id_str
    writer.commit()
    update_newest(db, g.user['id'], newest_id)

    return redirect(url_for('index'))


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
