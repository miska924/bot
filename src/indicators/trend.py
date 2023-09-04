import pandas as pd
from . import Indicator


class Trend(Indicator):
    def calculate(self, data: pd.DataFrame):
        left = data.head(data.shape[0] // 2).close.mean()
        right = data.tail(data.shape[0] - 1 - data.shape[0] // 2).close.mean()
        return left, right


    def to_plot(self, data: pd.DataFrame):
        result = []
        left, right = self.calculate(data)
        tmp = pd.DataFrame(
            [
                dict(value=left),
                dict(value=right),
            ],
        )
        tmp.index = [
            data.index[data.index.get_loc(data.index[data.shape[0] // 4])],
            data.index[data.index.get_loc(data.index[data.shape[0] - 1 - data.shape[0] // 4])],
        ]
        result.append(tmp)
        return result

    