from . import AbstractClient

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException

import logging
import datetime as dt
import pandas as pd
import math


CANDLE_INTERPOLATION_STEPS = 12


def emulate_candle(candle: pd.core.series.Series, progress: float):
    result = candle.copy()
    result.low = candle.open
    result.high = candle.open

    if candle.open > candle.close:
        #      high
        # open      \     close
        #            \   /
        #             low
        if progress * 3 < 1.0:  # open -> low
            first = 1.0 - progress * 3
            second = progress * 3
            result.close = first * candle.open + second * candle.high
            result.high = result.close
        elif progress * 3 < 2.0:  # low -> high
            first = 2.0 - progress * 3
            second = progress * 3 - 1.0
            result.close = first * candle.high + second * candle.low
            result.high = candle.high
            result.low = min(result.low, result.close)
        else:  # high -> close
            first = 3.0 - progress * 3
            second = progress * 3 - 2.0
            result.close = first * candle.low + second * candle.close
            result.low = candle.low
            result.high = candle.high
    else:
        #           high
        # open     /    \
        #     \   /      close
        #      low
        if progress * 3 < 1.0:
            first = 1.0 - progress * 3
            second = progress * 3
            result.close = first * candle.open + second * candle.low
            result.low = result.close
        elif progress * 3 < 2.0:
            first = 2.0 - progress * 3
            second = progress * 3 - 1.0
            result.close = first * candle.low + second * candle.high
            result.low = candle.low
            result.high = max(result.high, result.close)
        else:
            first = 3.0 - progress * 3
            second = progress * 3 - 2.0
            result.close = first * candle.high + second * candle.close
            result.low = candle.low
            result.high = candle.high

    return result


class BacktesterClient(AbstractClient):
    def __init__(
        self,
        data: pd.DataFrame = None,
    ):
        self.index = 0
        self.data = data.copy()

        self.using_amount = 0
        self.target_amount = 100

        self.using = "BTC"
        self.target = "USDT"
        self.symbol = "BTCUSDT"

        self.min_qty = 0.00000100
        self.precision = 8
        self.min_notional = 10
        self.max_notional = 9000000

        self.comission = 0.0005
        self.progress = 0.0
        self.current_candle_step = 0

    def _iterate(self) -> None:
        self.current_candle_step += 1
        if self.current_candle_step == CANDLE_INTERPOLATION_STEPS + 1:
            self.current_candle_step = 0
            self.index += 1
        self.progress = self.current_candle_step / CANDLE_INTERPOLATION_STEPS

    def next(self) -> bool:
        self._iterate()
        return self.index < self.data.shape[0] and self.balance()["sum"] > 0

    def time(self) -> dt.datetime:
        cur = self.data.iloc[self.index]
        nxt = self.data.iloc[min(self.data.shape[0] - 1, self.index + 1)]

        return dt.datetime.fromtimestamp(
            nxt.time * self.progress + cur.time * (1.0 - self.progress)
        )

    def last(self, count: int, offset: int = 0, time: dt.datetime = None):
        assert offset >= 0
        time = time if time else self.time()

        avaliable = self.data.iloc[: self.index]
        emulated_last = emulate_candle(self.data.iloc[self.index], self.progress)
        avaliable = pd.concat([avaliable, pd.DataFrame([emulated_last])])
        avaliable = avaliable[avaliable.index <= time]
        return avaliable.tail(count + offset).head(count)

    def load(
        self,
        start: dt.datetime,
        end: dt.datetime,
    ) -> pd.DataFrame:
        avaliable = self.data.iloc[: self.index]
        emulated_last = emulate_candle(self.data.iloc[self.index], self.progress)
        avaliable = pd.concat([avaliable, pd.DataFrame([emulated_last])])
        return avaliable[start.timestamp() <= avaliable.time <= end.timestamp()]

    def price(self) -> float:
        return emulate_candle(self.data.iloc[self.index], self.progress).close

    def _order(self, quantity: str) -> None:
        quantity: float = float(quantity)
        self.using_amount += quantity
        volume = self.price() * quantity
        self.target_amount -= volume + self.comission * abs(volume)

    def asset_balance(self, asset: str) -> float:
        if asset == "USDT":
            # logging.info(f"USDT: {self.target_amount}")
            return self.target_amount
        elif asset == "BTC":
            # logging.info(f"BTC: {self.target_amount}")
            return self.using_amount

        raise NameError("No such asset")
