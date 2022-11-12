import datetime
from flask import Flask, render_template, request
from flask_restful import Api, Resource
import datetime

import BinanceApi
from Cache import PricesCache
from OptionModel import download_data_single, calculate_volatility, calculate_return_log
from OptionPriceMonteCarlo import OptionPricing

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


class OptionCalculation(Resource):

    def get(self):
        print("New Option request...")
        args = request.args
        stock_name = args.get('stock')

        expiry = None
        option_type = None
        try:
            expiry = self.get_expiry(args)
            option_type = self.get_option_type(args)
        except Exception as e:
            bad_request = {
                "error": e
            }
            return bad_request, 400

        option_price, stock_price, strike, strike_pct = self.calculate_option(expiry, stock_name, option_type)

        price = {
            "stock": stock_name,
            "expiry": "{}y".format(expiry),
            "type": option_type,
            "option_price": "{0:.3f}".format(option_price),
            "stock_price": "{0:.3f}".format(stock_price),
            "strike": "{0:.3f}".format(strike),
            "strike_pct": "{0:.2f}".format(strike_pct)
        }

        print("Option calculated...")
        return price, 200

    def get_option_type(self, args):
        option_type = args.get('opt_type')
        valid_type = option_type in ["put", "call"]
        if not valid_type:
            raise Exception("Invalid type {}".format(valid_type))
        return option_type

    def get_expiry(self, args):
        expiry = args.get('expiry')
        try:
            return int(expiry)
        except Exception as e:
            raise Exception("Invalid expiry {}, {}".format(expiry, e))

    def get_today(self):
        current_date = datetime.date.today()
        return current_date.strftime("%Y-%m-%d")

    def calculate_option(self, expiry, stock_name, option_type):
        prices = download_data_single(stock_name, '2010-01-01', self.get_today())
        stock_price = float(prices.tail(1)['Close'])
        print("Stock price: ", stock_price)
        strike = stock_price * 1
        strike_pct = 100 * 1
        print("Strike level {}: ".format(strike))
        print("Strike pct {}%: ".format(strike_pct))
        print("Expiry {}y: ".format(expiry))
        risk_free_rate = 0.006  # switzerland
        returns = calculate_return_log(prices)
        volatility = calculate_volatility(prices)
        print("Volatility: ", volatility)
        model = OptionPricing(stock_price, strike, expiry, risk_free_rate, volatility, 1000)
        if option_type == 'call':
            option_price = model.call_option_simulation()
        else:
            option_price = model.put_option_simulation()
        return option_price, stock_price, strike, strike_pct


app = Flask(__name__)
api = Api(app)
api.add_resource(Exchange, "/api/rest/prices")
api.add_resource(OptionCalculation, "/api/rest/option_prices")


@app.route('/')
def index():
    return render_template('index.html')



app.run(host="0.0.0.0", debug=True, use_reloader=False, port=80)

