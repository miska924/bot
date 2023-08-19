import pandas as pd

from . import AbstractStrategy, Position
from src.indicators import Indicator


class NothingStrategy(AbstractStrategy):
    def __init__(
        self,
        indicators: list,
    ):
        self._indicators: list(Indicator) = indicators
    
    def indicators(self, data: pd.DataFrame) -> tuple[list, list]:
        res: list[pd.DataFrame] = []
        for indicator in self._indicators:
            res.append(indicator.calculate(data))
        return res, []

    def action(self, data: pd.DataFrame, position: Position) -> Position:
        return None
