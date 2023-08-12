import pandas as pd
from enum import Enum


class Action(Enum):
    LONG = 0
    NONE = 1
    SHORT = 2


class AbstractStrategy:
    def __init__(self):
        pass

    def action(self, data: pd.DataFrame, position: bool) -> tuple[Action, list[float]]:
        raise NotImplementedError

    def up_stops(self) -> list[float]:
        return [0.01]

    def bottom_stops(self) -> list[float]:
        return [-0.01]


class Combination(AbstractStrategy):
    def __init__(self, strategies):
        self.strategies = strategies

    def action(self, data: pd.DataFrame, position: bool) -> Action:
        actions = []
        for strategy in self.strategies:
            actions.append(strategy.action(data, position))

        if all([action == Action.LONG for action in actions]):
            return Action.LONG
        if all([action == Action.SHORT for action in actions]):
            return Action.SHORT
        if any([action == Action.NONE for action in actions]):
            return Action.NONE
        return None

    def up_stops(self) -> list[float]:
        stops = []
        for strategy in self.strategies:
            stops += strategy.up_stops()

    def bottom_stops(self) -> list[float]:
        stops = []
        for strategy in self.strategies:
            stops += strategy.bottom_stops()
