import pandas as pd
from . import Indicator


class Max(Indicator):
    def __init__(self, period: int, column="close"):
        self.period = period
        self.column = column

    def calculate(self, data: pd.DataFrame):
        return data[self.column].rolling(window=self.period).max()


class Min(Indicator):
    def __init__(self, period: int, column="close"):
        self.period = period
        self.column = column

    def calculate(self, data: pd.DataFrame):
        return data[self.column].rolling(window=self.period).min()
