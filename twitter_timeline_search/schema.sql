DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS tweet;
DROP TABLE IF EXISTS newest_tweet;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  twitter_consumer_key TEXT NOT NULL,
  twitter_consumer_secret TEXT NOT NULL,
  twitter_access_token TEXT NOT NULL,
  twitter_access_token_secret TEXT NOT NULL
);

CREATE TABLE tweet (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  id_str TEXT,
  created TIMESTAMP NOT NULL,
  author_name TEXT NOT NULL,
  author_screen_name TEXT NOT NULL,
  text TEXT NOT NULL,
  json TEXT NOT NULL,
  FOREIGN KEY (user_id) REFERENCES user (id)
);

CREATE TABLE newest_tweet (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  id_str TEXT NOT NULL,
  FOREIGN KEY (user_id) REFERENCES user (id)
);
