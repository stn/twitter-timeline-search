import os
import tweepy

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from twitter_timeline_search.auth import login_required
from twitter_timeline_search.db import get_db, get_newest, store_status, update_newest


bp = Blueprint('tweet', __name__)

@bp.route('/')
@login_required
def index():
    db = get_db()
    statuses = db.execute('SELECT * FROM tweet WHERE user_id = ?',
                          (g.user['id'],)).fetchall()
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
    since_id = get_newest(db)
    newest_id = None
    for status in tweepy.Cursor(api.home_timeline, since_id=since_id).items(3):
        store_status(db, status, g.user['id'])
        if newest_id is None:
            newest_id = status.id_str
    update_newest(db, g.user['id'], newest_id)

    return redirect(url_for('index'))
