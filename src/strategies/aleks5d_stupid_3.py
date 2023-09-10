import pandas as pd

from . import AbstractStrategy, Position
from src.indicators.ema import EMA


class Aleks5dStupid3(AbstractStrategy):
    def __init__(
        self,
        window: int = 10,
        swap_disbalance: float = 0.02,
        continue_disbalance: float = 0.06,
        alpha: float = 0.05,
        profit: float = 1,
        loss: float = 2,
    ):
        assert 0.0 <= alpha <= 100.0
        assert 0 < window

        self.loss = loss
        self.profit = profit
        self.alpha = alpha
        self.swap_disbalance = swap_disbalance
        self.continue_disbalance = continue_disbalance
        self.window = window
        
        self.stop_loss_df = None
        self.take_profit_df = None
        self.take_profit = None
        self.stop_loss = None

    def calc_swap_plot(self, data: pd.DataFrame):
        return data.close.rolling(window=2).apply(
                    lambda x: (x.iloc[0] - x.iloc[1]) / max(x.iloc[0], x.iloc[1])
                ).rolling(window=self.window).apply(
                    lambda x: x.sum()
                )


    def to_plot(self, data: pd.DataFrame) -> tuple[list, list]:
        if self.stop_loss_df is None:
            self.stop_loss_df = data.copy().close
            self.take_profit_df = data.copy().close
        else:
            self.stop_loss_df = pd.concat([self.stop_loss_df, pd.Series([data.close.iloc[-1]], index=[data.index[-1]])])
            self.take_profit_df = pd.concat([self.take_profit_df, pd.Series([data.close.iloc[-1]], index=[data.index[-1]])])
        if self.stop_loss is not None:
            self.stop_loss_df.iloc[-1] = self.stop_loss
            self.take_profit_df.iloc[-1] = self.take_profit
        return [
            self.stop_loss_df,
            self.take_profit_df
        ], [
            self.calc_swap_plot(data)
        ]
    
    def recalc(self):
        if self.stop_loss < self.take_profit:
            self.stop_loss += self.init_percent * self.alpha
            self.take_profit -= self.init_percent * self.alpha
        else:
            self.stop_loss -= self.init_percent * self.alpha
            self.take_profit += self.init_percent * self.alpha
    
    def LONG(self, close):
        self.take_profit = close * (100 + self.profit) / 100
        self.stop_loss = close * (100 - self.loss) / 100
        self.init_percent = close / 100
    
    def SHORT(self, close):
        self.take_profit = close * (100 - self.profit) / 100
        self.stop_loss = close * (100 + self.loss) / 100
        self.init_percent = close / 100
    
    def NONE(self):
        self.take_profit = None
        self.stop_loss = None
        self.init_percent = None

    def action(self, data: pd.DataFrame, position: Position) -> Position:
        close = data.iloc[-1].close

        if position == Position.LONG:
            self.recalc()
            if close < self.stop_loss or close > self.take_profit:
                self.NONE()
                return Position.NONE
            # return Position.LONG
        if position == Position.SHORT:
            self.recalc()
            if close < self.take_profit or close > self.stop_loss:
                self.NONE()
                return Position.NONE
            # return Position.SHORT

        balance = self.calc_swap_plot(data).iloc[-1] 

        if balance >= self.continue_disbalance:
            self.SHORT(close)
            return Position.SHORT
        if balance <= -self.continue_disbalance:
            self.LONG(close)
            return Position.LONG
        if balance >= self.swap_disbalance:
            self.LONG(close)
            return Position.LONG
        if balance <= -self.swap_disbalance:
            self.SHORT(close)
            return Position.SHORT

        return position
        
