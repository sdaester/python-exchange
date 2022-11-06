#https://python-binance.readthedocs.io/en/latest/binance.html#binance.client.Client.get_klines

from binance import Client
import threading
from time import sleep
import ElasticRest
import json

import logging

from Cache import PricesCache

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(process)d [%(levelname)s] %(name)s: %(message)s')

THROTTLE = 2

SUBSCRIPTIONS = {
    'BNB',
    'BTC',
    'ETH',
    'SOL',
    'XRP',
    'ADA'
}


def get_ids():
    return SUBSCRIPTIONS


class ThreadSafeSingleton (type):
    _instances = {}
    _singleton_lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        # double-checked locking pattern (https://en.wikipedia.org/wiki/Double-checked_locking)
        if cls not in cls._instances:
            with cls._singleton_lock:
                if cls not in cls._instances:
                    cls._instances[cls] = super(ThreadSafeSingleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class BinanceAPIClient(threading.Thread, metaclass=ThreadSafeSingleton):

    def __init__(self, prices_cache, ids='BNB', cross_ccy='USDT'):
        BinanceAPIClient.__instance = self
        threading.Thread.__init__(self)
        self.client = Client()
        self.prices_cache = prices_cache
        self.ids = ids
        self.cross_ccy = cross_ccy
        self.running = True

        self.index_name = 'trades'

    def retrieve_prices(self):
        logging.info("retrieve_prices")
        prices = {}
        for id in self.ids:
            symbol = id + self.cross_ccy
            price = self.client.get_avg_price(symbol=symbol)
            prices[symbol] = price['price']
        logging.info(prices)
        return prices

    def refresh_cache(self):
        prices_resp = self.retrieve_prices()
        for symbol in prices_resp:
            price = prices_resp[symbol]
            self.prices_cache.set(symbol, price)
        self.retrieve_trades()

    def run(self):
        while self.running:
            self.refresh_cache()
            sleep(THROTTLE)

    def stop(self):
        self.running = False;

    def update_elastic(self, symbol, trades):
        for trade in trades:
            date = ElasticRest.create_date_from_unix(trade['time'])
            trade['@timestamp'] = date
            trade['symbol'] = symbol
            trade['qty'] = float(trade['qty'])
            trade['price'] = float(trade['price'])
            #print(date)
            ElasticRest.insert(self.index_name, trade['id'], trade)

    def retrieve_trades(self):
        for id in self.ids:
            symbol = id + self.cross_ccy
            trades = self.client.get_recent_trades(symbol=symbol)
            self.update_elastic(symbol, trades)

def start_price_client(prices_cache):
    client = BinanceAPIClient(prices_cache, ids=SUBSCRIPTIONS)
    client.start()
    print('BinanceAPIClient has Started...')


if __name__ == "__main__":
    print("running in main...")
    prices_cache = PricesCache()
    start_price_client(prices_cache)
