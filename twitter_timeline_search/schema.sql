DROP TABLE IF EXISTS user;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  twitter_consumer_key TEXT NOT NULL,
  twitter_consumer_secret TEXT NOT NULL,
  twitter_access_token TEXT NOT NULL,
  twitter_access_token_secret TEXT NOT NULL
);
