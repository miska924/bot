import pandas as pd

from . import AbstractStrategy, Action


class ReversalsStrategy(AbstractStrategy):
    def __init__(self, wait: int = 1, reaction: int = 1, window: int = 15):
        self.ttl = 0
        self.wait = wait
        self.reaction = reaction
        self.window = window

    def action(self, data: pd.DataFrame, position: bool) -> Action:
        if data.shape[0] < 10:
            return None
        if self.ttl:
            self.ttl -= 1
            # return None if self.ttl else Action.NONE

        closes: pd.Series = data.head(data.shape[0] - self.reaction).close
        highs: pd.Series = data.head(data.shape[0] - self.reaction).high
        lows: pd.Series = data.head(data.shape[0] - self.reaction).low

        close_min_index = lows.argmin()
        close_max_index = highs.argmax()
        # print(lows)
        # print(close_min_index)
        # print(highs)
        # print(close_max_index)
        # exit(1)

        prev = data.close.iloc[-self.reaction]
        last = data.close.iloc[-1]

        if closes.size - close_min_index < self.window and all(
            [
                data.close.iloc[-i - 1] < lows.iloc[close_min_index]
                for i in range(self.reaction)
            ]
        ):
            self.ttl = self.wait
            return Action.LONG
        elif closes.size - close_max_index < self.window and all(
            [
                data.close.iloc[-i - 1] > highs.iloc[close_max_index]
                for i in range(self.reaction)
            ]
        ):
            self.ttl = self.wait
            return Action.SHORT

        return None
