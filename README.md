I created this script to archive USDT/USD trade data on kraken.com, however, it now works with any currency pair, as long as you update the get_alt_pair_name() function.

To use the script edit the kraken_data_file path in `get_data.py` or leave as is and it will save data in the current directory. Then run `python get_data.py --get-trades --pair USDTUSD` and `python get_data.py --get-spreads --pair USDTUSD` periodically (could be setup as a cronjob). To print a csv run `python get_data.py --print-trades --pair USDTUSD > ./output/USDTUSD-trades.csv`

```
usage: get_data.py [-h] [--get-trades] [--get-spreads] [--print-trades]
                   [--print-spreads] [--graph-trades] [--graph-spreads]
                   [--graph-net-buying] [--graph-net-buying-adjusted]
                   [--trades-summary] [--trade-histogram]
                   [--print-unique-trade-volumes]
                   [--graph-unique-trade-volumes] [--pair PAIR]

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
  --graph-net-buying    graph all net buying
  --graph-net-buying-adjusted
                        graph all net buying adjusted
  --trades-summary      print a summary of trades
  --trade-histogram     show a histogram of trades
  --print-unique-trade-volumes
                        print all unique trade volumes as a csv
  --graph-unique-trade-volumes
                        graph all unique trade volumes
  --pair PAIR           input a kraken currency
                        pair(USDTUSD,XBTUSD,ETHUSD,etc), default is USDTUSD
```

BTC Donations: 38hs9PyTbWG4SgyS4yvrR8CQ9PFXErJ5xk
