import pandas as pd
from . import Indicator

from enum import Enum


GROUP_BY = 0.05


class OptType(Enum):
    MIN = 0
    MAX = 1


def diff(a: pd.DataFrame, b: pd.DataFrame, opt_type: OptType, strict=False):
    if opt_type == OptType.MIN:
        result = a < b
    elif opt_type == OptType.MAX:
        result = a > b
    else:
        raise NotImplementedError
    if not strict:
        result |= b.isna()
    return result


def group(values, eps):
    return values
    values = sorted(values)
    last_group = [values[0]]
    result = []
    for i in range(1, len(values)):
        if values[i] - values[i - 1] < eps:
            last_group.append(values[i])
        else:
            result.append(sum(last_group) / len(last_group))
            last_group = [values[i]]

    result.append(sum(last_group) / len(last_group))
    return result


class Optimum(Indicator):
    def __init__(self, opt_type: OptType, column: str = "close", count: int = 2):
        assert count > 0
        self.count = count
        self.column = column
        self.opt_type = opt_type

    def calculate(self, data: pd.DataFrame):
        sz = data.shape[0]
        mx = data[self.column].max()
        mn = data[self.column].min()

        mask = data[self.column] == data[self.column]
        for shift in range(1, sz):
            mask &= diff(
                data[self.column], data.shift(shift)[self.column], self.opt_type
            )
            mask &= diff(
                data[self.column], data.shift(-shift)[self.column], self.opt_type
            )

            if (
                len(group(data[mask][self.column].to_list(), (mx - mn) * GROUP_BY))
                <= self.count
            ):
                break

        return group(data[mask][self.column].to_list(), (mx - mn) * GROUP_BY)

    def to_plot(self, data: pd.DataFrame):
        result = []
        for optimum in self.calculate(data):
            tmp = pd.DataFrame(
                [
                    dict(value=optimum),
                    dict(value=optimum),
                ],
            )
            tmp.index = [data.index[0], data.index[-1]]
            result.append(tmp)
        return result


class Support(Optimum):
    def __init__(self, count: int = 2):
        super().__init__(opt_type=OptType.MIN, column="low", count=count)


class Resistance(Optimum):
    def __init__(self, count: int = 2):
        super().__init__(opt_type=OptType.MAX, column="high", count=count)
