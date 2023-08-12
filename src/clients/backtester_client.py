from . import AbstractClient

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException

import logging
import datetime as dt
import pandas as pd
import math

PRICE_ITERATIONS = 10


class BacktesterClient(AbstractClient):
    def __init__(self, data: pd.DataFrame, interval="1m"):
        self.index = 0
        self.data = data

        self.using_amount = 0
        self.target_amount = 100

        self.using = "BTC"
        self.target = "USDT"
        self.symbol = "BTCUSDT"
        self.interval = interval

        self.min_qty = 0.00000100
        self.precision = 8
        self.min_notional = 10
        self.max_notional = 9000000

        self.comission = 0.0001
        self.up_stops = set()
        self.bottom_stops = set()
        self.position = False

        self.price_iteration = 0
        self.last_price = self._price()

    def check_stops(self):
        # return
        for i in range(PRICE_ITERATIONS):
            super().check_stops()
            self.price_iteration = i
        self.price_iteration = 0

    def current(self) -> dict:
        return self.data.iloc[self.index]

    def next(self) -> bool:
        self.check_stops()
        self.index += 1
        # logging.info(self.data.shape)
        return self.index < self.data.shape[0] and self.balance()["sum"] > 0

    def time(self) -> dt.datetime:
        current_time = dt.datetime.fromtimestamp(self.data.iloc[self.index].time)
        return current_time

    def load(self, start: dt.datetime, end: dt.datetime) -> pd.DataFrame:
        result = self.data[
            (self.data.time >= start.timestamp()) & (self.data.time <= end.timestamp())
        ]
        return result

    def _price(self) -> float:
        return self.data.iloc[self.index].close
        # (
        #     self.data.iloc[self.index].close * (PRICE_ITERATIONS - self.price_iteration)
        #     + self.data.iloc[min(self.data.shape[0] - 1, self.index + 1)].close
        #     * self.price_iteration
        # ) / PRICE_ITERATIONS

    def _order(self, quantity: str) -> None:
        quantity: float = float(quantity)
        self.using_amount += quantity
        volume = self._price() * quantity
        self.target_amount -= volume + self.comission * abs(volume)

    def _asset_balance(self, asset: str) -> float:
        if asset == "USDT":
            # logging.info(f"USDT: {self.target_amount}")
            return self.target_amount
        elif asset == "BTC":
            # logging.info(f"BTC: {self.target_amount}")
            return self.using_amount

        raise NameError("No such asset")
