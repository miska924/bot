import pandas as pd
from . import Indicator


class EMA(Indicator):
    def __init__(self, period: int):
        self.period = period
        pass

    def calculate(self, data: pd.DataFrame):
        return data.ewm(span=self.period, adjust=False).mean()
