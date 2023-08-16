import pandas as pd

from . import AbstractStrategy, Position


class ReversalsV2Strategy(AbstractStrategy):
    def __init__(self, window: int = 10, position_ttl=12000, threshold=0.2):
        self.window = window
        self._up_stops = []
        self._bottom_stops = []
        self.long_entry = None
        self.short_entry = None
        self.entry_ttl = 0
        self.threshold = threshold
        self.position_ttl = 0
        self.position_ttl_limit = position_ttl

    def up_stops(self) -> list[float]:
        return self._up_stops

    def bottom_stops(self) -> list[float]:
        return self._bottom_stops

    def buy_up(self) -> list[float]:
        res = [self.long_entry] if self.long_entry else []
        # print(res)
        return res

    def sell_bottom(self) -> list[float]:
        res = [self.short_entry] if self.short_entry else []
        # print(res)
        return res

    def action(self, data: pd.DataFrame, position: bool) -> Position:
        if position:
            if not self.position_ttl:
                self.position_ttl = self.position_ttl_limit
            self.short_entry = None
            self.long_entry = None
            self.position_ttl -= 1
            if not self.position_ttl:
                print("oh(")
                return Position.NONE
            return None
        self.position_ttl = 0

        if self.entry_ttl:
            self.entry_ttl -= 1
            if self.entry_ttl == 0:
                self.long_entry = None
                self.short_entry = None
        # print(data.shape, position)

        size = data.shape[0]

        if size < 100:
            return None

        high: pd.Series = data.iloc[-1].high
        low: pd.Series = data.iloc[-1].low
        close: pd.Series = data.iloc[-1].close

        min_index = data.iloc[:-1].low.argmin()
        max_index = data.iloc[:-1].high.argmax()
        _min = float(data.low.iloc[min_index])
        _max = float(data.high.iloc[max_index])

        # if self.entry_ttl == 0:
        #     self.long_entry = None
        #     self.short_entry = None

        # if _max - _min < _min * 0.005:
        #     return None

        # print("hello")

        if (
            _max - _min > _min * 0.001
            and low < _min
            and 5 < size - min_index < self.window
        ):
            # for i in range(size):
            #     print(data.iloc[i])
            self.short_entry = None
            self.long_entry = high
            # print("long", high)
            self.entry_ttl = self.window
        elif (
            _max - _min > _min * 0.001
            and high > _max
            and 5 < size - max_index < self.window
        ):
            # for i in range(size):
            #     print(data.iloc[i])
            self.short_entry = low
            self.long_entry = None
            # print("short", low)
            self.entry_ttl = self.window

        if self.long_entry:
            # _min = data.iloc[max_index:].low.min()
            self._bottom_stops = [_min]
            if min_index < self.window:
                self.long_entry = None
            elif self.long_entry >= _max or self.long_entry <= _min:
                self.long_entry = None
            elif (self.long_entry - _min) * 5 > (_max - self.long_entry):
                self.long_entry = None
            else:
                # _min = max(_min, self.long_entry * 0.999)
                _max = self.long_entry + (self.long_entry - _min) * 5
                self._bottom_stops = [_min]
                self._up_stops = [_max]
        elif self.short_entry:
            # _max = data.iloc[min_index:].high.max()
            if max_index < self.window:
                self.short_entry = None
            elif self.short_entry >= _max or self.short_entry <= _min:
                self.short_entry = None
            elif (_max - self.short_entry) * 5 > (self.short_entry - _min):
                self.short_entry = None
            else:
                # _max = min(_max, self.short_entry * 1.001)
                _min = self.short_entry - (_max - self.short_entry) * 5
                self._bottom_stops = [_min]
                self._up_stops = [_max]

            # if self.long_entry and close > self.long_entry:
            #     if _max - close < (close - _min) * 1:
            #         self.long_entry = None
            #         return None

            #     self._up_stops = [_max - (_max - _min) * self.threshold]
            #     self.long_entry = None
            #     # self._bottom_stops = [data.iloc[min_index].low]
            #     self.position_ttl = self.position_ttl_limit
            #     return None

            # if self.short_entry and close < self.short_entry:
            #     if close - _min < (_max - close) * 1:
            #         self.short_entry = None
            #         return None
            #     self._bottom_stops = [_min + (_max - _min) * self.threshold]
            #     # self._up_stops = [data.iloc[max_index].high]
            #     self.short_entry = None
            #     self.position_ttl = self.position_ttl_limit
            #     return None

        return None
