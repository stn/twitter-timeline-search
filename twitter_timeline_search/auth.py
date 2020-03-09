import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from twitter_timeline_search.db import get_db


bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        twitter_consumer_key = request.form['twitter_consumer_key']
        twitter_consumer_secret = request.form['twitter_consumer_secret']
        twitter_access_token = request.form['twitter_access_token']
        twitter_access_token_secret = request.form['twitter_access_token_secret']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif not twitter_consumer_key:
            error = 'Twitter Consumer Key is required.'
        elif not twitter_consumer_secret:
            error = 'Twitter Consumer Secret is required.'
        elif not twitter_access_token:
            error = 'Twitter Access Token is required.'
        elif not twitter_access_token_secret:
            error = 'Twitter Access Token Secret is required.'
        elif db.execute(
            'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone() is not None:
            error = 'User {} is already registered.'.format(username)

        if error is None:
            db.execute('''INSERT INTO user (
                username
                , password
                , twitter_consumer_key
                , twitter_consumer_secret
                , twitter_access_token
                , twitter_access_token_secret
                ) VALUES (?, ?, ?, ?, ?, ?)''',
                       (username,
                        generate_password_hash(password),
                        twitter_consumer_key,
                        twitter_consumer_secret,
                        twitter_access_token,
                        twitter_access_token_secret))
            db.commit()
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            session['twitter_consumer_key'] = user['twitter_consumer_key']
            session['twitter_consumer_secret'] = user['twitter_consumer_secret']
            session['twitter_access_token'] = user['twitter_access_token']
            session['twitter_access_token_secret'] = user['twitter_access_token_secret']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view

