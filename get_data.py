#!/usr/bin/python
from argparse import ArgumentParser
import os
import requests
import pickle
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime
import pytz

def to_dt(dt):
    return datetime.datetime.utcfromtimestamp(float(dt)).replace(tzinfo=pytz.UTC)

def get_data(api_keyword, last):
    """ Make a kraken API request and return the json data or print an error """
    url = "{}{}?pair=USDTUSD".format(api_url, api_keyword)
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

def save_kraken_vars_to_file(last_trades_req, last_spreads_req, trades, spreads):
    with open(kraken_data_file, 'wb') as f:
        pickle.dump([last_trades_req, last_spreads_req, trades, spreads], f)

def load_kraken_vars_from_file():
    with open(kraken_data_file, 'rb') as f:
        return pickle.load(f)

def print_kraken(data):
    for time in data:
        print(",".join([str(time)] + data[time]))

def get_trades(last_trades_req, last_spreads_req, trades, spreads):
    data = get_data("Trades", last_trades_req)
    for trade in data["result"]["USDTZUSD"]:
        price, volume, time, buy_or_sell, market_or_limit, misc = trade
        trades[time] = [price, volume, buy_or_sell, market_or_limit, misc]
    last_trades_req = data["result"]["last"]
    save_kraken_vars_to_file(last_trades_req, last_spreads_req, trades, spreads)

def get_spreads(last_trades_req, last_spreads_req, trades, spreads):
    data = get_data("Spread", last_spreads_req)
    for spread in data["result"]["USDTZUSD"]:
        time, bid, ask = spread
        spreads[time] = [bid, ask]
    last_spreads_req = data["result"]["last"]
    save_kraken_vars_to_file(last_trades_req, last_spreads_req, trades, spreads)

def graph(data_type, data):
    x,y,y2 = [],[],[]
    for time in sorted(data):
        x.append(to_dt(time))
        y.append(float(data[time][0]))
        if data_type == "Spreads":
            y2.append(float(data[time][1]))
    fig, ax = plt.subplots()
    if data_type == "Spreads":
        plt.plot_date(x, y, '-', color="blue", label="bid")
        plt.plot_date(x, y2, '-', color="orange", label="ask")
    else:
        plt.plot_date(x, y, '-', color="blue", label="trade")
    myFmt = mdates.DateFormatter('%m-%d')
    ax.xaxis.set_major_formatter(myFmt)
    plt.legend()
    plt.locator_params(axis='y', nticks=4)
    title = "USDT/USD kraken.com {} history".format(data_type)
    plt.title(title)
    plt.xlabel("Time")
    plt.ylabel("Price")
    plt.savefig("./" + title.replace("/","-") + ".png")
    plt.show()

api_url = "https://api.kraken.com/0/public/"
kraken_data_file = "./kraken_data.pkl"

# Create tmp kraken data file if it doesn't exist yet
if os.path.isfile(kraken_data_file) is False:
    # create 
    last_trades_req = ""
    last_spreads_req = ""
    trades = {}
    spreads = {}
    save_kraken_vars_to_file(last_trades_req, last_spreads_req, trades, spreads)

last_trades_req, last_spreads_req, trades, spreads = load_kraken_vars_from_file()

aparser = ArgumentParser()
#_ is used as a throwaway variable name
_ = aparser.add_argument('--get-trades', action='store_true', dest="get_trades", help='hit kraken.com api and get all recent USDT/USD trades and save them in {}'.format(kraken_data_file), required=False)
_ = aparser.add_argument('--get-spreads', action='store_true', dest="get_spreads", help='hit kraken.com api and get all recent USDT/USD spreads and save them in {}'.format(kraken_data_file), required=False)
_ = aparser.add_argument('--print-trades', action='store_true', dest="print_trades", help='print all stored USDT/USD trades as a csv', required=False)
_ = aparser.add_argument('--print-spreads', action='store_true', dest="print_spreads", help='print all stored USDT/USD spreads as a csv', required=False)
_ = aparser.add_argument('--graph-trades', action='store_true', dest="graph_trades", help='graph all stored USDT/USD trades', required=False)
_ = aparser.add_argument('--graph-spreads', action='store_true', dest="graph_spreads", help='graph all stored USDT/USD spreads', required=False)
args = aparser.parse_args()

if args.get_trades:
    get_trades(last_trades_req, last_spreads_req, trades, spreads)
if args.get_spreads:
    get_spreads(last_trades_req, last_spreads_req, trades, spreads)
if args.print_trades:
    print("time,price,volume,buy_or_sell,market_or_limit,misc")
    print_kraken(trades)
if args.print_spreads:
    print("time,bid,ask")
    print_kraken(spreads)
if args.graph_trades:
    graph("Trades", trades)
if args.graph_spreads:
    graph("Spreads", spreads)
