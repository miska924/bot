import pandas as pd
from . import Indicator


class Max(Indicator):
    def __init__(self, period: int = None, column="close"):
        self.period = period
        self.column = column

    def calculate(self, data: pd.DataFrame):
        if self.period is None:
            return data[self.column].max()

        return data[self.column].tail(self.period).max()

    def to_plot(self, data: pd.DataFrame):
        return data[self.column].rolling(window=self.period).max()


class Min(Indicator):
    def __init__(self, period: int = None, column="close"):
        self.period = period
        self.column = column

    def calculate(self, data: pd.DataFrame):
        if self.period is None:
            return data[self.column].min()

        return data[self.column].tail(self.period).min()

    def to_plot(self, data: pd.DataFrame):
        return data[self.column].rolling(window=self.period).max()
