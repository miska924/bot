import pandas as pd


class Indicator:
    def __init__(self):
        pass

    def calculate(self, data: pd.DataFrame):
        raise NotImplementedError

    def to_plot(self, data: pd.DataFrame):
        return self.calculate(data=data)
