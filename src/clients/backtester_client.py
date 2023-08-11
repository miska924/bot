from . import AbstractClient

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException

import logging
import datetime as dt
import pandas as pd
import math


class BacktesterClient(AbstractClient):
    def __init__(self, data: pd.DataFrame, interval="1m"):
        self.index = 0
        self.data = data

        self.using_amount = 0
        self.target_amount = 1000

        self.using = "BTC"
        self.target = "USDT"
        self.symbol = "BTCUSDT"
        self.interval = interval

        self.min_qty = 0.00000100
        self.precision = 8
        self.min_notional = 1
        self.max_notional = 9000000

        self.comission = 0.0001

    def next(self) -> bool:
        self.index += 1
        # logging.info(self.data.shape)
        return self.index < self.data.shape[0]

    def time(self) -> dt.datetime:
        current_time = dt.datetime.fromtimestamp(
            self.data.head(self.index).tail(1).time.values[0]
        )
        return current_time

    def load(self, start: dt.datetime, end: dt.datetime) -> pd.DataFrame:
        result = self.data[
            (self.data.time >= start.timestamp()) & (self.data.time <= end.timestamp())
        ]
        return result

    def _price(self):
        return self.data.iloc[self.index].close

    def _order(self, quantity: str) -> None:
        quantity = float(quantity)
        self.using_amount += quantity
        volume = self._price() * quantity
        self.target_amount -= volume + self.comission * abs(volume)

    def _asset_balance(self, asset: str) -> float:
        if asset == "USDT":
            return self.target_amount
        elif asset == "BTC":
            return self.using_amount

        raise NameError("No such asset")
