import pandas as pd
from . import Indicator


class Imbalance(Indicator):
    
    def calculate(self, data: pd.DataFrame):
        tmp = data.copy()
        tmp['imbalance'] = None
        tmp['imbalance_up'] = tmp.shift(-1).low - tmp.shift(1).high
        tmp['imbalance_down'] = tmp.shift(1).low - tmp.shift(-1).high
        
        tmp['imbalance_bottom'] = (tmp['imbalance_up'] > 0) * tmp.shift(1).high + (tmp['imbalance_down'] > 0) * tmp.shift(-1).high
        tmp['imbalance_top'] = (tmp['imbalance_up'] > 0) * tmp.shift(-1).low + (tmp['imbalance_down'] > 0) * tmp.shift(1).low
        
        tmp = tmp[tmp['imbalance_top'] - tmp['imbalance_bottom'] > 0][['imbalance_bottom', 'imbalance_top']]
        return tmp['imbalance_bottom'], tmp['imbalance_top']


    def to_plot(self, data: pd.DataFrame):
        result = []
        bottoms, tops = self.calculate(data)
        for i in range(bottoms.shape[0]):
            tmp = pd.DataFrame(
                [
                    dict(value=bottoms.iloc[i]),
                    dict(value=bottoms.iloc[i]),
                    dict(value=tops.iloc[i]),
                    dict(value=tops.iloc[i]),
                ],
            )
            tmp.index = [
                data.index[data.index.get_loc(bottoms.index[i]) - 1],
                data.index[data.index.get_loc(bottoms.index[i]) + 1],
                data.index[data.index.get_loc(bottoms.index[i]) - 1],
                data.index[data.index.get_loc(bottoms.index[i]) + 1],
            ]
            result.append(tmp)
        return result

    