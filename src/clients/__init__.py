import pandas as pd
import datetime as dt
import math
from enum import Enum
import logging


def sign(x: float) -> int:
    return 1 if x > 0 else -1


class AbstractClient:
    def __init__(self, **kwargs):
        pass

    def load(self, start: dt.datetime, end: dt.datetime) -> pd.DataFrame:
        raise NotImplementedError()

    def _price(self) -> float:
        raise NotImplementedError()

    def _order(self, quantity: str):
        raise NotImplementedError()

    def current(self):
        raise NotImplementedError

    def set_using_part(self, using_part: float):
        self.position = using_part != 0
        # print(self.in_position())
        price = self._price()
        balance = self.balance()

        amount = balance["sum"] * using_part - balance[self.using] * price
        quantity = float(amount / price)

        if abs(quantity * price) < self.min_notional:
            return
        if abs(quantity * price) > self.max_notional:
            quantity = sign(quantity) * self.max_notional / price

        parts = quantity / self.min_qty
        parts = int(math.ceil(parts) if parts < 0 else math.floor(parts))
        quantity = float(parts * self.min_qty)

        self._order(
            quantity=f"{quantity:0.{self.precision}f}",
        )
        self.last_price = price

    def in_position(self):
        return self.position

    def set_up_stops(self, stops: list):
        self.up_stops = set(stops)

    def set_bottom_stops(self, stops: list):
        self.bottom_stops = set(stops)

    def check_stops(self):
        price = self._price()

        for stop in self.up_stops:
            if price > stop:
                self.set_using_part(0)
                self.up_stops = set()
                self.bottom_stops = set()

        for stop in self.bottom_stops:
            if price < stop:
                self.set_using_part(0)
                self.up_stops = set()
                self.bottom_stops = set()

    def _asset_balance(self, asset: str) -> float:
        raise NotImplementedError()

    def balance(self) -> dict:
        using_amount = self._asset_balance(asset=self.using)
        target_amount = self._asset_balance(asset=self.target)

        return {
            self.using: using_amount,
            self.target: target_amount,
            "sum": target_amount + using_amount * self._price(),
        }

    def next(self) -> bool:
        self.check_stops()

        return True

    def time(self):
        return dt.datetime.now()
