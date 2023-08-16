import pandas as pd
from random import randint

from . import AbstractStrategy, Position


class RandomStrategy(AbstractStrategy):
    def __init__(self):
        pass

    def action(self, data: pd.DataFrame, position: bool) -> Position:
        action = randint(0, 2)
        if action == 0:
            return Position.LONG
        elif action == 1:
            return Position.SHORT

        return Position.NONE
