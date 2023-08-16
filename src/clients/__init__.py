import pandas as pd
import datetime as dt
import math
from enum import Enum
import logging
import time

from src.strategies import Position


def sign(x: float) -> int:
    return 1 if x > 0 else -1


class AbstractClient:
    def __init__(self, **kwargs):
        pass

    def load(self, start: dt.datetime, end: dt.datetime) -> pd.DataFrame:
        raise NotImplementedError

    def price(self) -> float:
        raise NotImplementedError

    def _order(self, quantity: str):
        raise NotImplementedError

    def set_using_part(self, using_part: float):
        # print(self.in_position())
        price = self.price()
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
        # self.last_price = price

    def position(self):
        balance = self.balance()
        if balance["sum"] * 0.999 < balance[self.target] < balance["sum"] * 1.001:
            return Position.NONE
        if balance[self.using] > 0:
            return Position.LONG
        if balance[self.using] < 0:
            return Position.SHORT

        assert True

    def asset_balance(self, asset: str) -> float:
        raise NotImplementedError()

    def balance(self) -> dict:
        using_amount = self.asset_balance(asset=self.using)
        target_amount = self.asset_balance(asset=self.target)

        return {
            self.using: using_amount,
            self.target: target_amount,
            "sum": target_amount + using_amount * self.price(),
        }

    def get_target(self) -> str:
        return self.target

    def get_using(self) -> str:
        return self.using

    def next(self) -> bool:
        return True

    def time(self):
        return dt.datetime.now(dt.timezone.utc)
