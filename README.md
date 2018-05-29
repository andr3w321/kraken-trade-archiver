I created this script to archive USDT/USD trade data on kraken.com, however, it now works with any currency pair, as long as you update the get_alt_pair_name() function.

To use the script

Create sqlite3 database `sqlite3 db.sql < create-sql-tables.sql` or download and use the current db.sql file. The db.sql is over 100 MB now. Contact me or open an issue if you want a copy of the db instead of the csvs.

Run `python get_data.py --get-trades --pair USDTUSD` and `python get_data.py --get-spreads --pair USDTUSD` periodically (could be setup as a cronjob). To print a csv run `python get_data.py --print-trades --pair USDTUSD > ./output/USDTUSD-trades.csv`

```
usage: get_data.py [-h] [--db-file DB_FILE] [--get-trades] [--get-spreads]
                   [--print-trades] [--print-spreads] [--graph-trades]
                   [--graph-spreads] [--graph-net-buying]
                   [--graph-net-buying-adjusted] [--trades-summary]
                   [--trade-histogram] [--print-unique-trade-volumes]
                   [--graph-unique-trade-volumes] [--pair PAIR]

optional arguments:
  -h, --help            show this help message and exit
  --db-file DB_FILE     input the path to db file, the default is ./db.sql
  --get-trades          hit kraken.com api and get all recent trades and save
                        them in db
  --get-spreads         hit kraken.com api and get all recent spreads and save
                        them in db
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
