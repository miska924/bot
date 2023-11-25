import pandas as pd

from . import AbstractStrategy, Position
from src.indicators import Indicator
from src.indicators.extremum import Min, Max


class ReversalsStrategy(AbstractStrategy):
    def __init__(
        self,
        window: int = 120,
        peak_distance: int = 30,
        indicators: list = [],
        risk_reward: float = 3,
    ):
        self.window = window
        self.peak_distance = peak_distance
        self._indicators: list(Indicator) = indicators
        self.risk_reward = risk_reward

        self.entry_position = None
        self.entry = None

    def indicators(self, data: pd.DataFrame) -> tuple[list, list]:
        res: list[pd.DataFrame] = []
        for indicator in self._indicators:
            res.append(indicator.calculate(data))
        return res, []

    def in_position_action(self, data: pd.DataFrame, position: Position) -> Position:
        close = data.iloc[-1].close
        if position == Position.LONG:
            if close < self.stop_loss or close > self.take_profit:
                return Position.NONE
            return None
        elif position == Position.SHORT:
            if close > self.stop_loss or close < self.take_profit:
                return Position.NONE
            return None

        raise Exception(f"Do not know what to do with current position: {position}")

    def waiting_entry(self, data) -> Position:
        # print("waiting_entry")
        last = data.iloc[-1]
        if self.entry_position == Position.LONG:
            if last.low < self.stop_loss:
                self.stop_loss = last.low

            if abs(self.entry - self.stop_loss) * self.risk_reward > abs(
                self.take_profit - self.entry
            ):
                self.entry_position = None
                return None

            if self.entry < last.close:
                pos = self.entry_position
                self.entry_position = None
                return pos

            return None
        elif self.entry_position == Position.SHORT:
            if last.high > self.stop_loss:
                self.stop_loss = last.high

            if abs(self.entry - self.stop_loss) * self.risk_reward > abs(
                self.take_profit - self.entry
            ):
                self.entry_position = None
                return None

            if last.close < self.entry:
                pos = self.entry_position
                self.entry_position = None
                return pos

            return None

        raise Exception(
            f"Do not know what to do with entry position: {self.entry_position}"
        )

    def action(self, data: pd.DataFrame, position: Position) -> Position:
        if position != Position.NONE:
            return self.in_position_action(data, position)

        if self.entry_position != None:
            return self.waiting_entry(data)

        if data.shape[0] < 2:
            return None

        last = data.iloc[-1]
        tail = data.iloc[: data.shape[0] - 1]

        mn = Min(self.window, "low").calculate(tail)
        mx = Max(self.window, "high").calculate(tail)
        tail_peak_mn = (
            tail.tail(self.peak_distance).head(self.peak_distance - 3).low.min()
        )
        tail_peak_mx = (
            tail.tail(self.peak_distance).head(self.peak_distance - 3).high.max()
        )

        if mn < last.low and last.high < mx:
            return None

        possible_position = None

        if last.close < mn and mn == tail_peak_mn:
            stop = last.low
            take = mx
            possible_position = Position.LONG

        if mx < last.close and mx == tail_peak_mx:
            stop = last.high
            take = mn
            possible_position = Position.SHORT

        if possible_position is not None:
            # print(f"possible {possible_position}")
            if abs(last.open - stop) * self.risk_reward > abs(take - last.open):
                return None

            if possible_position is not None:
                # print(possible_position, last.open)
                self.entry_position = possible_position
                self.entry = last.open

                self.stop_loss = stop
                self.take_profit = take

        return None
