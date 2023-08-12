import pandas as pd
from random import randint

from . import AbstractStrategy, Action


class RandomStrategy(AbstractStrategy):
    def __init__(self):
        pass

    def action(self, data: pd.DataFrame, position: bool) -> Action:
        action = randint(0, 2)
        if action == 0:
            return Action.LONG
        elif action == 1:
            return Action.SHORT

        return Action.NONE
