class PricesCache:

    def __init__(self):
        self.__cache__ = {}

    def set(self, symbol, price):
        self.__cache__[symbol] = price

    def get(self, symbol):
        return self.__cache__.get(symbol, None)