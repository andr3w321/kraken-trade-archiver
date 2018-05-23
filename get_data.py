#!/usr/bin/python
from argparse import ArgumentParser
import os
import requests
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime
import pytz
import numpy
import math
import sqlite3
from sqlite3 import Error

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

def get_last_req(cur, trade_or_spreads, pair):
    if trade_or_spreads not in ["trade","spreads"]:
        raise ValueError("trade_or_spreads arg must be 'trade' or 'spreads'")
    else:
        query = """SELECT last_""" + trade_or_spreads + """_req FROM global WHERE pair = ?"""
        cur.execute(query, (pair,))
        rows = cur.fetchall()
        if len(rows) < 1:
            return ""
        else:
            return rows[0][0]

def upsert_last_req(cur, trade_or_spreads, pair, last):
    if trade_or_spreads not in ["trade","spreads"]:
        raise ValueError("trade_or_spreads arg must be 'trade' or 'spreads'")
    else:
        query = """INSERT OR IGNORE INTO global (pair, last_""" + trade_or_spreads + """_req) VALUES (?,?)"""
        cur.execute(query, (pair, last))
        query = """UPDATE global SET last_""" + trade_or_spreads + """_req = ? WHERE pair = ?"""
        cur.execute(query, (last, pair))

def get_db_trades(cur, pair):
    cur.execute("""SELECT * FROM trade WHERE pair = ? ORDER BY unix_time""",(pair,))
    return cur.fetchall()

def get_db_spreads(cur, pair):
    cur.execute("""SELECT * FROM spread WHERE pair = ? ORDER BY unix_time""",(pair,))
    return cur.fetchall()

def get_alt_pair_name(pair):
    # Use https://api.kraken.com/0/public/AssetPairs to lookup altname if want to add pairs
    if pair == "USDTUSD":
        return "USDTZUSD"
    elif pair == "XBTUSD":
        return "XXBTZUSD"
    elif pair == "ETHUSD":
        return "XETHZUSD"
    elif pair in ["BCHUSD","EOSUSD"]:
        return pair
    else:
        print("ERROR: Unknown pair {}".format(pair))

def to_dt(dt):
    return datetime.datetime.utcfromtimestamp(float(dt)).replace(tzinfo=pytz.UTC)

def get_data(pair, api_keyword, last):
    """ Make a kraken API request and return the json data or print an error """
    url = "{}{}?pair={}".format(api_url, api_keyword, pair)
    if last != "":
        url = "{}&since={}".format(url, last)
    print(url)
    res = requests.get(url)
    if res.status_code == 200:
        data = res.json()
        if data["error"] != []:
            print("ERROR", data["error"])
        else:
            return data
    else:
        print("ERROR:", res.status_code)

def print_kraken(pair, data):
    for row in data:
        print(",".join([str(x) for x in list(row)]))

def get_trades(pair, cur):
    data = get_data(pair, "Trades", get_last_req(cur, "trade", pair))
    for trade in data["result"][get_alt_pair_name(pair)]:
        price, volume, unix_time, buy_or_sell, market_or_limit, misc = trade
        upsert_trade(cur, pair, unix_time, price, volume, buy_or_sell, market_or_limit, misc)
    upsert_last_req(cur, "trade", pair, data["result"]["last"])

def get_spreads(pair, cur):
    data = get_data(pair, "Spread", get_last_req(cur, "spreads", pair))
    for spread in data["result"][get_alt_pair_name(pair)]:
        unix_time, bid, ask = spread
        upsert_spread(cur, pair, unix_time, bid, ask)
    upsert_last_req(cur, "spreads", pair, data["result"]["last"])

def graph(pair, data_type, data):
    x,y,y2 = [],[],[]
    net_buys = 0
    for row in data:
        if len(row) == 8: # Must be trades data
            id, pair, unix_time, price, volume, buy_or_sell, market_or_limit, misc = row
        elif len(row) == 5: # Must be spreads data
            id, pair, unix_time, bid, ask = row
        else:
            raise ValueError("Unknown data")
        x.append(to_dt(unix_time))
        if data_type.startswith("Net Buying"):
            volume = float(volume)
            price = float(price)
            if data_type == "Net Buying":
                if buy_or_sell == "b":
                    net_buys += price * volume
                elif buy_or_sell == "s":
                    net_buys -= price * volume
            elif data_type == "Net Buying Adjusted":
                # see which is closer to zero, a buy or a sell
                pv = price * volume
                if abs(net_buys + pv) < abs(net_buys - pv):
                    net_buys += pv
                else:
                    net_buys -= pv
            y.append(net_buys)
        else:
            y.append(float(row[3])) # price for trades data, bid for spreads data
        if data_type == "Spreads":
            y2.append(float(row[4]))
    fig, ax = plt.subplots()
    if data_type == "Spreads":
        plt.plot_date(x, y, '-', color="blue", label="bid")
        plt.plot_date(x, y2, '-', color="orange", label="ask")
    else:
        plt.plot_date(x, y, '-', color="blue", label="trade")
    myFmt = mdates.DateFormatter('%m-%d')
    ax.xaxis.set_major_formatter(myFmt)
    ax.get_yaxis().get_major_formatter().set_scientific(False)
    plt.legend()
    title = "{} kraken.com {} history".format(pair, data_type)
    plt.title(title)
    plt.xlabel("Time")
    if data_type.startswith("Net Buying"):
        plt.ylabel("Net Buying")
    else:
        plt.ylabel("Price")
    plt.savefig(output_folder + title.replace("/","-") + ".png")
    plt.show()

def trades_summary(pair, data):
    buys, sells, market_orders, limit_orders, total_volume, n_trades = 0,0,0,0,0,0
    for row in data:
        id, pair, unix_time, price, volume, buy_or_sell, market_or_limit, misc = row
        volume = float(volume)
        price = float(price)
        n_trades += 1
        total_volume += volume
        if buy_or_sell == "b":
            buys += 1
        elif buy_or_sell == "s":
            sells +=1
        if market_or_limit == "m":
            market_orders += 1
        elif market_or_limit == "l":
            limit_orders += 1
    print("{} Trade Summary".format(pair))
    print("Buy orders(vs Sell): {:.2f}% ({}/{})".format(buys/(buys + sells) * 100.0, buys, (buys + sells)))
    print("Market orders(vs Limit): {:.2f}% ({}/{})".format(market_orders/(market_orders + limit_orders) * 100.0, market_orders, (market_orders + limit_orders)))
    print("Total volume: {:,.2f} or ${:,.2f}".format(total_volume, price * total_volume))
    print("Total number of trades: {:,}".format(n_trades))
    trade_volumes = get_unique_trade_volumes(pair, data)
    print("Unique trade volume amounts: {:,} or {:,.2f}% ({:,}/{:,})\n".format(len(trade_volumes), len(trade_volumes) / n_trades * 100.0, len(trade_volumes), n_trades))

def trade_histogram(pair, data):
    # work in progress...
    x = []
    for row in data:
        id, pair, unix_time, price, volume, buy_or_sell, market_or_limit, misc = row
        price, volume, buy_or_sell, market_or_limit, misc = data[pair][time]
        volume = float(volume)
        x.append(volume)
    n, bins, patches = plt.hist(x, bins=5, normed=True, facecolor='g')
    plt.show()

def get_unique_trade_volumes(pair, data):
    # could be done much easier with sql query, but adapting old code for now cause its quicker
    trade_volumes = {}
    for row in data:
        id, pair, unix_time, price, volume, buy_or_sell, market_or_limit, misc = row
        volume = float(volume)
        if volume not in trade_volumes:
            trade_volumes[volume] = 1
        else:
            trade_volumes[volume] += 1
    return trade_volumes

def print_unique_trade_volumes(pair, data):
    trade_volumes = get_unique_trade_volumes(pair, data)
    print("Trade_volume,Number of trades with that volume")
    for trade_volume in trade_volumes:
        print("{},{}".format(str(trade_volume), trade_volumes[trade_volume]))

def graph_unique_trade_volumes(pair, data):
    trade_volumes = get_unique_trade_volumes(pair, data)
    x,y = [],[]
    for trade_volume in trade_volumes:
        x.append(math.log(trade_volume + 1))
        y.append(trade_volumes[trade_volume])
    plt.scatter(x,y)
    plt.xlabel("log(Unique Trade Volume + 1)")
    plt.ylabel("Number of trades at that exact volume")
    title = "{} unique trade volumes vs number of trades occuring at that volume".format(pair)
    plt.title(title)
    plt.savefig(output_folder + title.replace("/","-") + ".png")
    plt.show()

api_url = "https://api.kraken.com/0/public/"
output_folder = "./output3/"

aparser = ArgumentParser()
#_ is used as a throwaway variable name
_ = aparser.add_argument('--db-file', action='store', dest="db_file", help='input the path to db file, the default is ./db.sql', required=False)
_ = aparser.add_argument('--get-trades', action='store_true', dest="get_trades", help='hit kraken.com api and get all recent trades and save them in db', required=False)
_ = aparser.add_argument('--get-spreads', action='store_true', dest="get_spreads", help='hit kraken.com api and get all recent spreads and save them in db', required=False)
_ = aparser.add_argument('--print-trades', action='store_true', dest="print_trades", help='print all stored trades as a csv', required=False)
_ = aparser.add_argument('--print-spreads', action='store_true', dest="print_spreads", help='print all stored spreads as a csv', required=False)
_ = aparser.add_argument('--graph-trades', action='store_true', dest="graph_trades", help='graph all stored trades', required=False)
_ = aparser.add_argument('--graph-spreads', action='store_true', dest="graph_spreads", help='graph all stored spreads', required=False)
_ = aparser.add_argument('--graph-net-buying', action='store_true', dest="graph_net_buying", help='graph all net buying', required=False)
_ = aparser.add_argument('--graph-net-buying-adjusted', action='store_true', dest="graph_net_buying_adjusted", help='graph all net buying adjusted', required=False)
_ = aparser.add_argument('--trades-summary', action='store_true', dest="trades_summary", help='print a summary of trades', required=False)
_ = aparser.add_argument('--trade-histogram', action='store_true', dest="trade_histogram", help='show a histogram of trades', required=False)
_ = aparser.add_argument('--print-unique-trade-volumes', action='store_true', dest="print_unique_trade_volumes", help='print all unique trade volumes as a csv', required=False)
_ = aparser.add_argument('--graph-unique-trade-volumes', action='store_true', dest="graph_unique_trade_volumes", help='graph all unique trade volumes', required=False)
_ = aparser.add_argument('--pair', action='store', dest="pair", help='input a kraken currency pair(USDTUSD,XBTUSD,ETHUSD,etc), default is USDTUSD', required=False)
args = aparser.parse_args()

if args.pair is None:
    args.pair = "USDTUSD"
if args.db_file is None:
    args.db_file = "./db.sql"

conn = create_connection(args.db_file)
cur = conn.cursor()

if args.get_trades:
    get_trades(args.pair, cur)
if args.get_spreads:
    get_spreads(args.pair, cur)
if args.print_trades:
    print("time,price,volume,buy_or_sell,market_or_limit,misc")
    print_kraken(args.pair, get_db_trades(cur, args.pair))
if args.print_spreads:
    print("time,bid,ask")
    print_kraken(args.pair, get_db_spreads(cur, args.pair))
if args.graph_trades:
    graph(args.pair, "Trades", get_db_trades(cur, args.pair))
if args.graph_spreads:
    graph(args.pair, "Spreads", get_db_spreads(cur, args.pair))
if args.graph_net_buying:
    graph(args.pair, "Net Buying", get_db_trades(cur, args.pair))
if args.graph_net_buying_adjusted:
    graph(args.pair, "Net Buying Adjusted", get_db_trades(cur, args.pair))
if args.trades_summary:
    trades_summary(args.pair, get_db_trades(cur, args.pair))
if args.trade_histogram:
    trade_histogram(args.pair, get_db_trades(cur, args.pair))
if args.print_unique_trade_volumes:
    print_unique_trade_volumes(args.pair, get_db_trades(cur, args.pair))
if args.graph_unique_trade_volumes:
    graph_unique_trade_volumes(args.pair, get_db_trades(cur, args.pair))

conn.commit()
