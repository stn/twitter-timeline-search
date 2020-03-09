# twitter-timeline-search
Search your Twitter timeline


## Preliminary

A Twitter API tokens is needed for now.
Please apply them from https://developer.twitter.com/ .
But I'm not sure if 'want to use this' works.


## Install

```bash
git clone https://github.com/stn/twitter-timeline-search.git
cd twitter-timeline-search
```

for Pipenv users:

```bash
pipenv --python 3
pipenv install
pipenv shell
```

TODO: requirements.txt

## Initialize DB

```bash
flask init-db
flask init-search
```


## Run a server

```bash
export FLASK_APP=twitter_timeline_search
flask run
```
