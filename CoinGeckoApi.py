from pycoingecko import CoinGeckoAPI
from threading import Thread
from time import sleep

import logging

from Cache import PricesCache

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(process)d [%(levelname)s] %(name)s: %(message)s')

THROTTLE = 10

SUBSCRIPTIONS = {
    'bitcoin': 'btc',
    'litecoin': 'ltc',
    'ethereum': 'etc'
}


def get_ids():
    return lambda SUBSCRIPTIONS : SUBSCRIPTIONS.key()


class CoinGeckoAPIClient(Thread):

    def __init__(self, prices_cache, ids='bitcoin', cross_ccy='usd'):
        Thread.__init__(self)
        self.api_cg = CoinGeckoAPI()
        self.prices_cache = prices_cache
        self.ids = ids
        self.cross_ccy = cross_ccy

    def retrieve_prices(self):
        logging.info("retrieve_prices")
        prices = self.api_cg.get_price(self.ids, vs_currencies=self.cross_ccy)
        print(prices)
        return prices

    def refresh_cache(self):
        prices_resp = self.retrieve_prices()
        for ccy_id in prices_resp:
            ccy = SUBSCRIPTIONS[ccy_id]
            symbol = ccy + self.cross_ccy
            price = prices_resp[ccy_id][self.cross_ccy]
            self.prices_cache.set(symbol, price)

    def run(self):
        while True:
            self.refresh_cache()
            sleep(THROTTLE)


def start_price_client(prices_cache):
    client = CoinGeckoAPIClient(prices_cache, ids='bitcoin, litecoin, ethereum')
    client.start()
    print('Client has Started...')


if __name__ == "__main__":
    prices_cache = PricesCache()
    start_price_client(prices_cache)