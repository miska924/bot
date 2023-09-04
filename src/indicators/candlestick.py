import pandas as pd
from . import Indicator


PEAK = 0.05
TAIL = 0.7

class Hammer(Indicator):
    def __init__(self):
        pass

    def calculate(self, data: pd.DataFrame):
        size = (data.high - data.low)
        standard = size.mean()

        mask = ((data.high - data.low) > standard) & (
            (
                (data.open < data.close) & (
                    ((data.high - data.close < size * PEAK) & (data.open - data.low > size * TAIL)) |
                    ((data.open - data.low < size * PEAK) & (data.high - data.close > size * TAIL))
                )
            ) | (
                (data.close < data.open) & (
                    ((data.high - data.open < size * PEAK) & (data.close - data.low > size * TAIL)) |
                    ((data.close - data.low < size * PEAK) & (data.high - data.open > size * TAIL))
                )
            )
        )

        return data[mask | (data.index == data.index[0])][['close']]
