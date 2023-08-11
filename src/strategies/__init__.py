import pandas as pd
from enum import Enum


class Action(Enum):
    LONG = 0
    NONE = 1
    SHORT = 2


class AbstractStrategy:
    def __init__(self):
        pass

    def action(self, data: pd.DataFrame) -> Action:
        raise NotImplementedError


class Combination(AbstractStrategy):
    def __init__(self, strategies):
        self.strategies = strategies

    def action(self, data: pd.DataFrame) -> Action:
        actions = []
        for strategy in self.strategies:
            actions.append(strategy.action(data))

        if all([action == Action.LONG for action in actions]):
            return Action.LONG
        if all([action == Action.SHORT for action in actions]):
            return Action.SHORT
        if any([action == Action.NONE for action in actions]):
            return Action.NONE
        return None
