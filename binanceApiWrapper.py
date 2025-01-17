import hashlib
import hmac
import time
from collections import namedtuple

import requests
import ujson


class BinanceApiWrapper:
    def __init__(self, apiPublicKey="INSERT KEY", secretKey="INSERT KEY"):
        self.__publicKey = apiPublicKey
        self.__secretKey = secretKey

    def generate_signature(self, query_str):
        m = hmac.new(
            self.__secretKey.encode("utf-8"), query_str.encode("utf-8"), hashlib.sha256
        ).hexdigest()
        return m

    def get_apiKey(self):
        return self.__publicKey

    def get_secret_key(self):
        return self.__secretKey

    def get_traded_pairs(self):
        URL = "https://api.binance.com/api/v1/exchangeInfo"
        raw_response = requests.get(URL)
        try:
            parsed_response = (
                ujson.loads(raw_response.text) if raw_response is not None else None
            )
        except ValueError:
            return None

        if parsed_response is None:
            return None
        return parsed_response

    def place_sell_order(self, base_asset, quote_asset, quantity, sale_price=None):
        URL = "https://api.binance.com/api/v3/order"
        # URL = "https://api.binance.com/api/v3/order/test" uncomment to test
        symbol_pair = base_asset + quote_asset
        curr_time_msecs = int(time.time() * 1000)
        order_id = symbol_pair + str(curr_time_msecs)
        query_str = (
            "?symbol="
            + symbol_pair
            + "&timestamp="
            + str(curr_time_msecs)
            + "&side=SELL&type=LIMIT"
            + "&quantity="
            + str(quantity)
            + "&timeInForce=GTC"
            + "&price="
            + str(sale_price)
            + "&newClientOrderId="
            + order_id
        )
        sign = self.generate_signature(query_str[1:])
        header = {"X-MBX-APIKEY": self.get_apiKey()}
        raw_response = requests.post(
            URL + query_str + "&signature=" + (sign), headers=header
        )

        try:
            parsed_response = (
                ujson.loads(raw_response.text) if raw_response is not None else None
            )
        except ValueError:
            return None
        return parsed_response

    def place_buy_order(self, base_asset, quote_asset, quantity, buy_price=None):
        URL = "https://api.binance.com/api/v3/order"
        # URL = "https://api.binance.com/api/v3/order/test" uncomment to test
        symbol_pair = base_asset + quote_asset
        curr_time_msecs = int(time.time() * 1000)
        order_id = symbol_pair + str(curr_time_msecs)
        query_str = (
            "?symbol="
            + symbol_pair
            + "&timestamp="
            + str(curr_time_msecs)
            + "&side=BUY&type=LIMIT"
            + "&quantity="
            + str(quantity)
            + "&timeInForce=FOK"
            + "&price="
            + str(buy_price)
            + "&newClientOrderId="
            + order_id
        )
        sign = self.generate_signature(query_str[1:])
        header = {"X-MBX-APIKEY": self.get_apiKey()}
        raw_response = requests.post(
            URL + query_str + "&signature=" + (sign), headers=header
        )

        try:
            parsed_response = (
                ujson.loads(raw_response.text) if raw_response is not None else None
            )
        except ValueError:
            return None
        return parsed_response

    def current_open_orders(self, base_asset, quote_asset):
        URL = "https://api.binance.com/api/v3/openOrders"
        symbol_pair = base_asset + quote_asset
        curr_time_msecs = int(time.time() * 1000)
        query_str = "?symbol=" + symbol_pair + "&timestamp=" + str(curr_time_msecs)
        sign = self.generate_signature(query_str[1:])
        header = {"X-MBX-APIKEY": self.get_apiKey()}
        raw_response = requests.get(
            URL + query_str + "&signature=" + (sign), headers=header
        )
        try:
            parsed_response = (
                ujson.loads(raw_response.text) if raw_response is not None else None
            )
        except ValueError:
            return None
        if parsed_response is None:
            return None
        return parsed_response

    def get_kline_data(
        self,
        base_asset,
        quote_asset,
        interval="5m",
        start_msecs=None,
        end_msecs=None,
        limit=1000,
    ):
        URL = "https://api.binance.com/api/v1/klines"
        symbol_pair = base_asset + quote_asset
        if (start_msecs is not None) and (end_msecs is not None):
            query_str = (
                "?symbol="
                + symbol_pair
                + "&startTime="
                + str(start_msecs)
                + "&endTime="
                + str(end_msecs)
                + "&interval="
                + str(interval)
                + "&limit=1000"
            )
        else:
            query_str = (
                "?symbol="
                + symbol_pair
                + "&interval="
                + str(interval)
                + "&limit="
                + str(limit)
            )
        header = {"X-MBX-APIKEY": self.get_apiKey()}
        raw_response = requests.get(URL + query_str, headers=header)
        try:
            parsed_response = (
                ujson.loads(raw_response.text) if raw_response is not None else None
            )
        except ValueError:
            return None
        if parsed_response is None:
            return None

        column_names = [
            "open_timestamp",
            "quote_open_px",
            "quote_high_px",
            "quote_low_px",
            "quote_close_px",
            "base_volume",
            "close_timestamp",
            "quote_volume",
            "number_of_trades",
            "taker_base_volume",
            "taker_quote_volume",
            "interval",
        ]

        # use everything except ignore column, add interval
        Results = namedtuple("Results", column_names)
        kline_data = [Results._make(t[0:-1] + [interval]) for t in parsed_response]
        return kline_data
