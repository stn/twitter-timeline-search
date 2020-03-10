import os
from datetime import datetime, timedelta, timezone

from flask import Flask


JST = timezone(timedelta(hours=+9), 'JST')


def format_datetime(value):
    # TODO: timezone setting by user
    return value.replace(tzinfo=timezone.utc).astimezone(JST).strftime('%Y-%m-%d %H:%M:%S')


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'twitter.sqlite'),
        SEARCH=os.path.join(app.instance_path, 'twitter.whoosh'),
    )

    app.jinja_env.filters['datetime'] = format_datetime

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db
    db.init_app(app)

    from . import search
    search.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import tweet
    app.register_blueprint(tweet.bp)
    app.add_url_rule('/', endpoint='index')

    return app
