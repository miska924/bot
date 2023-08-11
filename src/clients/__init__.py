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

    def set_using_part(self, using_part: float):
        price = self._price()
        # logging.info(f"PRICE {price}")
        balance = self.balance()
        # logging.info(f"BALANCE {balance}")

        amount = balance["sum"] * using_part - balance[self.using] * price

        quantity = float(amount / price)
        # logging.info(quantity)

        if abs(quantity * price) < self.min_notional:
            # if using_part != 0:
            #     print(abs(quantity * price))
            return
        if abs(quantity * price) > self.max_notional:
            # logging.info("HELLO")
            quantity = sign(quantity) * self.max_notional / price

        # logging.info(quantity)
        # logging.info(self.min_qty)
        parts = quantity / self.min_qty
        # logging.info(parts)
        parts = int(math.ceil(parts) if parts < 0 else math.floor(parts))
        quantity = float(parts * self.min_qty)

        self._order(
            quantity=f"{quantity:0.{self.precision}f}",
        )
        self.last_price = price

    def check_stop(self):
        balance = self.balance()
        price = self._price()

        for stop in self.stops:
            if (
                (balance[self.using] < 0 and price < self.last_price)
                or (balance[self.using] > 0 and price > self.last_price)
            ) and stop > 0:
                if abs(price - self.last_price) > abs(stop):
                    self.set_using_part(0)
            elif (
                (balance[self.using] < 0 and price > self.last_price)
                or (balance[self.using] > 0 and price < self.last_price)
            ) and stop < 0:
                if abs(price - self.last_price) > abs(stop):
                    self.set_using_part(0)

            # if stop > 0:
            #     if (
            #         balance[self.using] < 0 and price < self.last_price * (1.0 - stop)
            #     ) or (
            #         balance[self.using] > 0 and price > self.last_price * (1.0 + stop)
            #     ):
            #         self.set_using_part(0)
            # else:
            #     if (
            #         balance[self.using] < 0 and price > self.last_price * (1.0 + stop)
            #     ) or (
            #         balance[self.using] > 0 and price < self.last_price * (1.0 - stop)
            #     ):
            #         self.set_using_part(0)

            # if (
            #     stop < 0
            #     and balance[self.using] > 0
            #     and price < self.last_price * (1.0 + stop)
            # ) or (
            #     stop > 0
            #     and balance[self.using] < 0
            #     and price > self.last_price * (1.0 + stop)
            # ):
            #     # logging.info(f"STOP ORDER {balance[self.using]}")
            #     self.set_using_part(0)

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
        self.check_stop()

        return True

    def time(self):
        return dt.datetime.now()
