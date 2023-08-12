import pandas as pd
from . import AbstractStrategy, Action


class ManualStrategy(AbstractStrategy):
    def __init__(self):
        pass

    def action(self, data: pd.DataFrame, position: bool) -> Action:
        action = input()

        if action == "long":
            return Action.LONG
        elif action == "short":
            return Action.SHORT

        return Action.NONE
