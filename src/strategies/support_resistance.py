import pandas as pd
from . import AbstractStrategy, Position
from src.indicators.optimum import Support, Resistance
from src.indicators.extremum import Max, Min


class SupportResistance(AbstractStrategy):
    def __init__(self):
        self.entry_position = None
        self.entry = None
        self.stop = None
        self.take = None

    def to_plot(self, data):
        resistances = Resistance(2).to_plot(data)
        supports = Support(2).to_plot(data)
        return resistances + supports, []

    def action(self, data: pd.DataFrame, position: Position):
        current = data.iloc[-1].close

        mx = Max().calculate(data)
        resistances = Resistance(2).calculate(data)
        supports = Support(2).calculate(data)
        mn = Min().calculate(data)

        allowed = (mx - mn) * 0.01

        if any([(current - support) < allowed for support in supports]):
            return Position.LONG if position != Position.LONG else None

        if any([(current - resistance) < allowed for resistance in resistances]):
            return Position.SHORT if position != Position.SHORT else None

        return None
