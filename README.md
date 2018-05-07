I created this script to archive USDT/USD trade data on kraken.com. I'm sure it could be adapted to other currency pairs easily with a fork.

To use the script edit the kraken_data_file path in `get_data.py` or leave as is and it will save data in the current directory. Then run `python get_data.py --get-trades` and `python get_data.py --get-spreads` periodically (could be setup as a cronjob). To print a csv run `python get_data.py --print-trades > trades.csv` or `python get_data.py --print-spreads > spreads.csv`

```
usage: get_data.py [-h] [--get-trades] [--get-spreads] [--print-trades]
                   [--print-spreads]

optional arguments:
  -h, --help       show this help message and exit
  --get-trades     hit kraken.com api and get all recent USDT/USD trades and
                   save them in ./kraken_data.pkl
  --get-spreads    hit kraken.com api and get all recent USDT/USD spreads and
                   save them in ./kraken_data.pkl
  --print-trades   print all stored USDT/USD trades as a csv
  --print-spreads  print all stored USDT/USD spreads as a csv
  --graph-trades   graph all stored USDT/USD trades
  --graph-spreads  graph all stored USDT/USD spreads
```

The graphs are currently a work in progress.
