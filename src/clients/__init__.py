import pandas as pd
import datetime as dt
import math
from enum import Enum


class AbstractClient:
    def __init__(self, **kwargs):
        pass

    def load(self, start: dt.datetime, end: dt.datetime) -> pd.DataFrame:
        raise NotImplementedError()

    def _price(self):
        raise NotImplementedError()

    def _order(self, quantity: str):
        raise NotImplementedError()

    def set_using_part(self, using_part: float):
        price = self._price()
        balance = self.balance()

        amount = balance["sum"] * using_part - balance[self.using] * price

        quantity = float(amount / price)

        if abs(quantity * price) < self.min_notional:
            # if using_part != 0:
            #     print(abs(quantity * price))
            return
        if abs(quantity * price) > self.max_notional:
            quantity = math.sign(quantity) * self.max_notional / price

        parts = quantity / self.min_qty
        parts = int(math.ceil(parts) if parts < 0 else math.floor(parts))
        quantity = float(parts * self.min_qty)

        self._order(
            quantity=f"{quantity:0.{self.precision}f}",
        )

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
