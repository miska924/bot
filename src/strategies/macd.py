import pandas as pd

from . import AbstractStrategy, Position
from src.indicators.ema import EMA
from src.indicators.ma import MA


class MACDStrategy(AbstractStrategy):
    def __init__(
        self,
        short_period: int = 12,
        long_period: int = 26,
        signal_period: int = 9,
        trend_period: int = 200,
        threshold: float = 0.0005,
    ):
        assert 0 < signal_period < short_period < long_period < trend_period
        assert 0.0 <= threshold <= 1.0

        self.short_period = short_period
        self.long_period = long_period
        self.signal_period = signal_period
        self.trend_period = trend_period
        self.threshold = threshold

        self.long = EMA(self.long_period)
        self.short = EMA(self.short_period)
        self.signal = EMA(self.signal_period)
        self.trend = EMA(self.trend_period)
        self.center = MA(long_period)

    def to_plot(self, data: pd.DataFrame) -> tuple[list, list]:
        df = data.copy()

        long_average = self.long.calculate(df.close)
        short_average = self.short.calculate(df.close)
        macd = short_average / long_average - 1

        return [
            self.trend.calculate(df.close),
        ], [
            (df.close - df.close).iloc[[0, -1]],
            macd,
            self.signal.calculate(macd),
        ]

    def action(self, data: pd.DataFrame, position: Position) -> Position:
        close = data.iloc[-1].close

        if position != Position.NONE:
            if position == Position.LONG:
                if close < self.stop_loss:
                    return Position.NONE
                if close > self.take_profit:
                    return Position.NONE
            if position == position.SHORT:
                if close > self.stop_loss:
                    return Position.NONE
                if close < self.take_profit:
                    return Position.NONE
            return None

        if data.shape[0] < self.long_period:
            return None
        df = data.copy()
        long_average = self.long.calculate(df.close)
        short_average = self.short.calculate(df.close)
        macd_series = short_average / long_average - 1
        macd = macd_series.iloc[-1]
        prev_macd = macd_series.tail(2).iloc[0]
        signal_series = self.signal.calculate(macd_series)
        signal: float = signal_series.iloc[-1]
        prev_signal: float = signal_series.tail(2).iloc[0]

        trend: float = self.trend.calculate(df.close).iloc[-1]

        # macd_last = macd.iloc[-1]
        # signal_last = signal.iloc[-1]

        if signal < macd:
            if (
                macd - signal > 0
                and macd < 0
                and prev_signal > prev_macd
                and close > trend
            ):
                # short_average.iloc[-1] < long_average.iloc[-1] and
                # short_average.tail(2).iloc[0] > long_average.tail(2).iloc[0] and
                # long_average.iloc[-1] < self.center.calculate(data=df.close).iloc[-1]
                res = Position.LONG if position != Position.LONG else None
            else:
                res = None if position != Position.SHORT else Position.NONE
        elif macd < signal:
            if (
                signal - macd > 0
                and macd > 0
                and prev_signal < prev_macd
                and close < trend
            ):
                # short_average.iloc[-1] > long_average.iloc[-1] and
                # short_average.tail(2).iloc[0] < long_average.tail(2).iloc[0] and
                # long_average.iloc[-1] > self.center.calculate(data=df.close).iloc[-1]
                res = Position.SHORT if position != Position.SHORT else None
            else:
                res = None if position != Position.LONG else Position.NONE

        # res = Position.NONE if position != Position.NONE else None
        local_min = df.close.tail(self.long_period).min()
        local_max = df.close.tail(self.long_period).max()

        if res == Position.LONG:
            self.stop_loss = local_min
            self.take_profit = local_max
            if close - local_min > 2 * (local_max - close):
                return None
        elif res == Position.SHORT:
            self.stop_loss = local_max
            self.take_profit = local_min
            if 2 * (close - local_min) < local_max - close:
                return None

        return res
