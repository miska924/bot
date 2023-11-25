import pandas as pd
from . import AbstractStrategy, Position
from src.indicators.optimum import Support, Resistance
from src.indicators.extremum import Max, Min


TTL = 30 * 3
NUM = 2


class SupportResistance(AbstractStrategy):
    def __init__(self):
        self.entry_position = None
        self.entry = None
        self.stop = None
        self.take = None
        self.ttl = 0

    def to_plot(self, data):
        resistances = Resistance(NUM).to_plot(data)
        supports = Support(NUM).to_plot(data)
        return resistances + supports, []

    def action(self, data: pd.DataFrame, position: Position):
        if self.ttl:
            self.ttl -= 1
            return None

        print(position)
        current = data.iloc[-1].close

        mx = Max().calculate(data)
        resistances = Resistance(NUM).calculate(data)
        supports = Support(NUM).calculate(data)
        mn = Min().calculate(data)

        allowed = (mx - mn) * 0.01

        if any([0 < (current - support) < allowed for support in supports]):
            self.ttl = TTL
            return Position.LONG

        if any([0 < (resistance - current) < allowed for resistance in resistances]):
            self.ttl = TTL
            return Position.SHORT

        return Position.NONE
