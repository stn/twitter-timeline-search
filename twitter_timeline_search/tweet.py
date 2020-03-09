import os
import tweepy

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from twitter_timeline_search.auth import login_required
from twitter_timeline_search.db import get_db


bp = Blueprint('tweet', __name__)

@bp.route('/')
@login_required
def index():
    auth = tweepy.OAuthHandler(g.user['twitter_consumer_key'],
                               g.user['twitter_consumer_secret'])
    auth.set_access_token(g.user['twitter_access_token'],
                          g.user['twitter_access_token_secret'])
    api = tweepy.API(auth, wait_on_rate_limit=True)
    statuses = tweepy.Cursor(api.home_timeline).items(10)
    return render_template('tweet/index.html', statuses=statuses)
