import pandas as pd
from enum import Enum


class Position(Enum):
    LONG = 0
    NONE = 1
    SHORT = 2


class AbstractStrategy:
    def __init__(self):
        pass

    def action(self, data: pd.DataFrame, in_position: bool) -> Position:
        raise NotImplementedError


class Combination(AbstractStrategy):
    def __init__(self, strategies):
        self.strategies = strategies

    def action(self, data: pd.DataFrame, in_position: bool) -> Position:
        actions = []
        for strategy in self.strategies:
            actions.append(strategy.action(data, in_position))

        if all([action == Position.LONG for action in actions]):
            return Position.LONG
        if all([action == Position.SHORT for action in actions]):
            return Position.SHORT
        if any([action == Position.NONE for action in actions]):
            return Position.NONE
        return None
