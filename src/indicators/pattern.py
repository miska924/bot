import pandas as pd
import numpy as np
from . import Indicator


# Checks if there is a local top detected at curr index
def rw_top(data: np.array, curr_index: int, order: int) -> bool:
    if curr_index < order * 2 + 1:
        return False

    top = True
    k = curr_index - order
    v = data[k]
    for i in range(1, order + 1):
        if data[k + i] > v or data[k - i] > v:
            top = False
            break

    return top


# Checks if there is a local top detected at curr index
def rw_bottom(data: np.array, curr_index: int, order: int) -> bool:
    if curr_index < order * 2 + 1:
        return False

    bottom = True
    k = curr_index - order
    v = data[k]
    for i in range(1, order + 1):
        if data[k + i] < v or data[k - i] < v:
            bottom = False
            break

    return bottom


def rw_extremes(data: pd.DataFrame, order: int) -> tuple[list, list]:
    # Rolling window local tops and bottoms
    tops = []
    bottoms = []
    for i in range(data.shape[0]):
        if rw_top(data.high.to_numpy(), i, order):
            # top[0] = confirmation index
            # top[1] = index of top
            # top[2] = price of top
            top = [i, i - order, data.iloc[i - order].high]
            tops.append(top)

        if rw_bottom(data.low.to_numpy(), i, order):
            # bottom[0] = confirmation index
            # bottom[1] = index of bottom
            # bottom[2] = price of bottom
            bottom = [i, i - order, data.iloc[i - order].low]
            bottoms.append(bottom)

    return tops, bottoms


class Patterns(Indicator):
    def __init__(self, order: int) -> None:
        self.order = order

    def calculate(self, data: pd.DataFrame) -> None:
        tops, bottoms = rw_extremes(data, self.order)

        indices, values = [], []

        i, j = 0, 0
        last_type = 0
        while i < len(tops) or j < len(bottoms):
            if i < len(tops) and (j == len(bottoms) or tops[i][1] < bottoms[j][1]):
                if last_type == 1:
                    if values[-1] < tops[i][2]:
                        indices[-1] = data.index[tops[i][1]]
                        values[-1] = tops[i][2]
                    i += 1
                    continue
                last_type = 1
                indices.append(data.index[tops[i][1]])
                values.append(tops[i][2])
            else:
                if last_type == -1:
                    if values[-1] > bottoms[j][2]:
                        indices[-1] = data.index[bottoms[j][1]]
                        values[-1] = bottoms[j][2]
                    j += 1
                    continue
                last_type = -1
                indices.append(data.index[bottoms[j][1]])
                values.append(bottoms[j][2])
                j += 1

        result = pd.DataFrame(values)
        result.index = indices
        return result

    def to_plot(self, data: pd.DataFrame) -> pd.DataFrame:
        return self.calculate(data)
