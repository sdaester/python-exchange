import datetime
from flask import Flask
from flask_restful import Api, Resource

import BinanceApi
from Cache import PricesCache

prices_cache = PricesCache()
BinanceApi.start_price_client(prices_cache)


class Exchange(Resource):

    def __init__(self):
        pass

    def get(self):
        global prices_cache
        prices = {
            "prices": prices_cache.__cache__,
            "timestamp": datetime.datetime.utcnow().isoformat()
        }
        return prices, 200


app = Flask(__name__)
api = Api(app)
api.add_resource(Exchange, "/api/rest/prices")
app.run(host="0.0.0.0", debug=True, use_reloader=False)

