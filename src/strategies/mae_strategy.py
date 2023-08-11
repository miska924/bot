import pandas as pd

from . import AbstractStrategy, Action


class MAEStrategy(AbstractStrategy):
    # def __init__(self, threshold=0.005):
    def __init__(self, threshold=0.0000):
        self.threshold = threshold

    def action(self, data: pd.DataFrame) -> Action:
        long_average = data.tail(24).close.mean()
        short_average = data.tail(12).close.mean()

        if short_average > long_average * (1 + self.threshold):
            return Action.LONG
        elif long_average > short_average * (1 + self.threshold):
            return Action.SHORT

        return Action.NONE
