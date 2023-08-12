import pandas as pd

from . import AbstractStrategy, Action


class ReversalsV2Strategy(AbstractStrategy):
    def __init__(self, window: int = 10):
        self.window = window
        self._up_stops = []
        self._bottom_stops = []
        self.long_entry = None
        self.short_entry = None
        self.entry_ttl = 0

    def up_stops(self) -> list[float]:
        return self._up_stops

    def bottom_stops(self) -> list[float]:
        return self._bottom_stops

    def action(self, data: pd.DataFrame, position: bool) -> Action:
        if position:
            return None
        # print(data.shape, position)

        size = data.shape[0]

        if size < 50:
            return None

        high: pd.Series = data.iloc[-1].high
        low: pd.Series = data.iloc[-1].low
        close: pd.Series = data.iloc[-1].close

        min_index = data.iloc[:-1].low.argmin()
        max_index = data.iloc[:-1].high.argmax()
        _min = float(data.low.iloc[min_index])
        _max = float(data.high.iloc[max_index])

        if self.entry_ttl == 0:
            self.long_entry = None
            self.short_entry = None

        if self.long_entry or self.short_entry:
            self.entry_ttl -= 1
            self._up_stops = [_max]
            self._bottom_stops = [_min]

            if self.long_entry and close > self.long_entry:
                self.long_entry = None
                self._up_stops = [data.iloc[max_index].close]
                return Action.LONG

            if self.short_entry and close < self.short_entry:
                self._bottom_stops = [data.iloc[min_index].close]
                self.short_entry = None
                return Action.SHORT

            return None

        if _max - _min < _min * 0.01:
            return None

        # print("hello")

        if low < _min and size - min_index < self.window:
            # for i in range(size):
            #     print(data.iloc[i])
            self.short_entry = None
            self.long_entry = high
            self.entry_ttl = self.window
        elif high > _max and size - max_index < self.window:
            # for i in range(size):
            #     print(data.iloc[i])
            self.short_entry = low
            self.long_entry = None
            self.entry_ttl = self.window

        return None
