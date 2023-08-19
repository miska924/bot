import pandas as pd
from . import Indicator

class MA(Indicator):
    def __init__(self, period: int):
        self.period = period
        pass
    
    def calculate(self, data: pd.DataFrame):
        return data.rolling(window=self.period).mean()