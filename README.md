I created this script to archive USDT/USD trade data on kraken.com, however, it now works with any currency pair, as long as you update the get_alt_pair_name() function.

To use the script edit the kraken_data_file path in `get_data.py` or leave as is and it will save data in the current directory. Then run `python get_data.py --get-trades` and `python get_data.py --get-spreads` periodically (could be setup as a cronjob). To print a csv run `python get_data.py --print-trades > trades.csv` or `python get_data.py --print-spreads > spreads.csv`

```
usage: get_data.py [-h] [--get-trades] [--get-spreads] [--print-trades]
                   [--print-spreads] [--graph-trades] [--graph-spreads]
                   [--trades-summary] [--trade-histogram]
                   [--unique-trade-volumes] [--pair PAIR]

optional arguments:
  -h, --help            show this help message and exit
  --get-trades          hit kraken.com api and get all recent trades and save
                        them in ./kraken_data.pkl
  --get-spreads         hit kraken.com api and get all recent spreads and save
                        them in ./kraken_data.pkl
  --print-trades        print all stored trades as a csv
  --print-spreads       print all stored spreads as a csv
  --graph-trades        graph all stored trades
  --graph-spreads       graph all stored spreads
  --trades-summary      print a summary of trades
  --trade-histogram     show a histogram of trades
  --unique-trade-volumes
                        print all unique trade volumes as a csv
  --pair PAIR           input a kraken currency
                        pair(USDTUSD,XBTUSD,ETHUSD,etc), default is USDTUSD
```

BTC Donations: 38hs9PyTbWG4SgyS4yvrR8CQ9PFXErJ5xk
