import pandas as pd

from . import AbstractStrategy, Action


class MAEStrategy(AbstractStrategy):
    def __init__(self, threshold=0.0001):
        self.threshold = threshold

    def action(self, data: pd.DataFrame) -> Action:
        long_average = data.tail(24).close.mean()
        mid_average = data.tail(12).close.mean()
        short_average = data.tail(6).close.mean()

        if mid_average > long_average * (1 + self.threshold):
            return Action.LONG
        elif mid_average > short_average * (1 + self.threshold):
            return Action.SHORT

        return None
