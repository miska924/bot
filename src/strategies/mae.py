import pandas as pd

from . import AbstractStrategy, Position


class MAEStrategy(AbstractStrategy):
    def __init__(self, short_period: int, long_period: int, threshold: float = 0.001):
        assert 0 < short_period < long_period
        assert 0.0 <= threshold <= 1.0

        self.short_period = short_period
        self.long_period = long_period
        self.threshold = threshold

    def action(self, data: pd.DataFrame, position: Position) -> Position:
        long_average = data.tail(self.long_period).close.mean()
        short_average = data.tail(self.short_period).close.mean()

        if abs(short_average - long_average) / long_average < self.threshold:
            return Position.NONE if position != Position.NONE else None

        if long_average < short_average:
            return Position.LONG if position != Position.LONG else None

        if long_average > short_average:
            return Position.SHORT if position != Position.SHORT else None

        return None
