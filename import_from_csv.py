import sqlite3
from sqlite3 import Error
import pandas as pd

### Short quick separate program to import trades or spreads from csv file

def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    return None

def upsert_trade(cur, pair, unix_time, price, volume, buy_or_sell, market_or_limit, misc):
    cur.execute("""INSERT OR IGNORE INTO trade(pair, unix_time, price, volume, buy_or_sell, market_or_limit, misc) VALUES (?,?,?,?,?,?,?)""", (pair, unix_time, price, volume, buy_or_sell, market_or_limit, misc))

def upsert_spread(cur, pair, unix_time, bid, ask):
    cur.execute("""INSERT OR IGNORE INTO spread(pair, unix_time, bid, ask) VALUES (?,?,?,?)""", (pair, unix_time, bid, ask))

db_file = "./db.sql"

conn = create_connection(db_file)
cur = conn.cursor()

"""
df = pd.read_csv("combined_output/combined-trades.csv")
for row in df.values:
    pair, unix_time, price, volume, buy_or_sell, market_or_limit, misc = row
    upsert_trade(cur, pair, unix_time, price, volume, buy_or_sell, market_or_limit, misc)
"""

df = pd.read_csv("combined_output/combined-spreads.csv")
for row in df.values:
    pair, unix_time, bid, ask = row
    upsert_spread(cur, pair, unix_time, bid, ask)

conn.commit()
