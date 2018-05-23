DROP TABLE IF EXISTS trade;
CREATE TABLE trade (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  pair VARCHAR(30),
  unix_time FLOAT,
  price FLOAT,
  volume FLOAT,
  buy_or_sell VARCHAR(5),
  market_or_limit VARCHAR(5),
  misc VARCHAR(100),
  CONSTRAINT trade_unique UNIQUE (pair, unix_time)
);

DROP TABLE IF EXISTS spread;
CREATE TABLE spread (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  pair VARCHAR(30),
  unix_time FLOAT,
  bid FLOAT,
  ask FLOAT,
  CONSTRAINT trade_unique UNIQUE (pair, unix_time)
);

DROP TABLE IF EXISTS global;
CREATE TABLE global(
  pair VARCHAR(30) PRIMARY KEY,
  last_trade_req INTEGER,
  last_spreads_req INTEGER
);
