from . import AbstractClient

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException

import logging
import datetime as dt
import pandas as pd
import math
from pytimeparse.timeparse import timeparse


class BinanceClient(AbstractClient):
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        target: str = "USDT",
        using: str = "BTC",
        interval: str = "1m",
        testnet: bool = True,
        stop: float = 0.01,
    ):
        self.using = using
        self.target = target
        self.symbol = f"{using}{target}"
        self.interval = interval
        self.api_key = api_key
        self.api_secret = api_secret
        self.client = Client(api_key, api_secret, testnet=testnet)
        self.stop = stop

        symbol_info = self.client.get_symbol_info(self.symbol)
        # logging.info(symbol_info)
        self.min_qty = float(symbol_info["filters"][1]["minQty"])
        self.precision = symbol_info["baseAssetPrecision"]
        self.min_notional = float(symbol_info["filters"][6]["minNotional"])
        self.max_notional = float(symbol_info["filters"][6]["maxNotional"])
        # self.max_leverage = self.client.get_max_margin_loan(asset=self.using)
        # logging.info(self.max_leverage)

    def last(self, count):
        window = dt.timedelta(seconds=timeparse(self.interval)) * (1000)
        end = self.time()
        start = end - window
        print(start, end)
        res = self.load(start, end)
        print(res)
        res.index = [dt.datetime.fromtimestamp(item) for item in res.time.to_list()]
        return res.tail(count)

    def load(self, start: dt.datetime, end: dt.datetime) -> pd.DataFrame:
        try:
            start_str: str = start.strftime("%Y-%m-%d %H:%M:%S")
            end_str: str = end.strftime("%Y-%m-%d %H:%M:%S")
            bars = self.client.get_historical_klines(
                self.symbol,
                self.interval,
                start_str,
                end_str,
            )
            # logging.info(start_str)
            # logging.info(end_str)
            # logging.info(bars)
        except BinanceAPIException as e:
            logging.error(f"Ошибка получения данных: {e}")
            return None

        data = []
        for b in bars:
            bar = {
                "time": b[0] / 1000,
                "open": float(b[1]),
                "high": float(b[2]),
                "low": float(b[3]),
                "close": float(b[4]),
                "volume": float(b[5]),
            }
            data.append(bar)
        result = pd.DataFrame(data)
        # print(result)
        return result

    def _order(self, quantity: str) -> None:
        try:
            if quantity < 0:
                order = self.client.order_market_sell(
                    symbol=self.symbol,
                    quantity=f"{-quantity:0.{self.precision}f}",
                )
            elif quantity > 0:
                order = self.client.order_market_buy(
                    symbol=self.symbol,
                    quantity=f"{+quantity:0.{self.precision}f}",
                )
        except BinanceAPIException as e:
            logging.error(f"Ошибка при открытии позиции: {e}")

        except BinanceOrderException as e:
            logging.error(f"Ошибка создания ордера: {e}")

    def price(self):
        try:
            price = self.client.get_symbol_ticker(symbol=self.symbol)
            return float(price["price"])

        except BinanceAPIException as e:
            logging.error(f"Ошибка получения цены: {e}")
            return None

    def asset_balance(self, asset: str) -> float:
        try:
            amount = self.client.get_asset_balance(asset=asset)
            return float(amount["free"])

        except (TypeError, KeyError, BinanceAPIException) as e:
            logging.error(f"Ошибка получения баланса: {e}")
            return None
