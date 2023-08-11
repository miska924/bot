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
