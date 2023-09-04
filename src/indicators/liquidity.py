import pandas as pd
from . import Indicator


EPS = 0.03

class Liquidity(Indicator):
    def calculate(self, data: pd.DataFrame):
        tmp = data.copy()
        diff = (data.high - data.low).mean()
        eps = EPS * diff
        
        mask = abs(data.low - data.shift(-1).low) < eps
        tmp['liq_low'] = (
            (data.low < data.shift(-1).low) * data.low +
            (data.low >= data.shift(-1).low) * data.shift(-1).low
        )
        return tmp[mask]['liq_low']


    def to_plot(self, data: pd.DataFrame):
        result = []
        lows = self.calculate(data)
        for i in range(lows.shape[0]):
            tmp = pd.DataFrame(
                [
                    dict(value=lows.iloc[i]),
                    dict(value=lows.iloc[i]),
                ],
            )
            tmp.index = [
                data.index[data.index.get_loc(lows.index[i])],
                data.index[data.index.get_loc(lows.index[i]) + 1],
            ]
            result.append(tmp)
        return result

    