import pandas as pd
from . import AbstractStrategy, Position


class ManualStrategy(AbstractStrategy):
    def __init__(self):
        pass

    def action(self, data: pd.DataFrame, position: bool) -> Position:
        action = input()

        if action == "long":
            return Position.LONG
        elif action == "short":
            return Position.SHORT

        return Position.NONE
