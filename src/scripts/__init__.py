import datetime as dt
import pandas as pd
import tqdm
import typing as tp
import matplotlib.pyplot as plt

from src.clients import AbstractClient
from src.strategies import AbstractStrategy, Position


def save_plot(
    indices: tp.List[dt.datetime],
    values: tp.List[list[float]],
    filename: str,
):
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(20, 5))
    ax.grid(True)
    fig.autofmt_xdate(rotation=45)
    for values_i in values:
        ax.plot(indices, values_i)

    fig.savefig(filename)
    plt.close(fig)


class Runner:
    def __init__(
        self,
        client: AbstractClient,
        strategy: AbstractStrategy,
        window: dt.timedelta,
        graph_filename: str = "tmp.png",
        long: float = 0.9,
        short: float = -0.9,
    ):
        self.client: AbstractClient = client
        self.strategy: AbstractStrategy = strategy
        self.window: dt.datetime = window

        self.graph_filename: str = graph_filename
        self.long: float = long
        self.short: float = short

    def _iteration(self) -> tuple[dt.datetime, float]:
        current_time = self.client.time()
        window_start_time = current_time - self.window

        data: pd.DataFrame = self.client.load(start=window_start_time, end=current_time)
        action: Position = self.strategy.action(data, self.client.in_position())

        if action == Position.LONG:
            self.client.set_using_part(self.long)
        elif action == Position.SHORT:
            self.client.set_using_part(self.short)
        elif action == Position.NONE:
            self.client.set_using_part(0)
        else:
            pass  # DO NOTHING

        self.client.set_up_stops(self.strategy.up_stops())
        self.client.set_bottom_stops(self.strategy.bottom_stops())
        self.client.set_buy_up(self.strategy.buy_up())
        self.client.set_sell_bottom(self.strategy.sell_bottom())

        return (
            current_time,
            self.client.balance()["sum"],
            self.client.balance()["BTC"],
        )

    @staticmethod
    def _save_graph(
        indices: tp.List[dt.datetime],
        values: tp.List[list[float]],
        filename: str,
        stocks: tp.List[dict] = None,
    ):
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(20, 5))

        ax.grid(True)
        fig.autofmt_xdate(rotation=45)
        top_money = max(values[0])
        bottom_money = min(values[0])
        for values_i in values[1:]:
            top = max(1e-6, max(values_i))
            bottom = min(-1e-6, min(values_i))
            ax.plot(
                indices,
                [
                    (item - bottom) / (top - bottom) * (top_money - bottom_money)
                    + (bottom_money)
                    for item in values_i
                ],
            )
        ax.plot(
            indices,
            values[0],
        )
        if stocks:
            stocks = pd.DataFrame(stocks, index=indices)
            print(stocks.index[-1])
            print(indices[-1])
            stocks[["open", "close", "high", "low"]] *= top_money / stocks.close.max()
            # print(stocks)
            # .reindex(["time"])

            up = stocks[stocks.close >= stocks.open]

            # "down" dataframe will store the stock_prices
            # when the closing stock price is
            # lesser than the opening stock prices
            down = stocks[stocks.close < stocks.open]

            ax.bar(up.index, (up.close - up.open), 0.002, bottom=up.open, color="green")
            ax.bar(
                up.index, (up.high - up.close), 0.0005, bottom=up.close, color="green"
            )
            ax.bar(up.index, (up.low - up.open), 0.0005, bottom=up.open, color="green")

            # Plotting down prices of the stock
            ax.bar(
                down.index,
                (down.close - down.open),
                0.002,
                bottom=down.open,
                color="red",
            )
            ax.bar(
                down.index,
                (down.high - down.open),
                0.0005,
                bottom=down.open,
                color="red",
            )
            ax.bar(
                down.index,
                (down.low - down.close),
                0.0005,
                bottom=down.close,
                color="red",
            )

        fig.savefig(filename)
        plt.close(fig)

    def run(self):
        indices = []
        balances = []
        btcs = []
        stocks = []

        for _ in tqdm.tqdm(range(self.client.data.shape[0])):
            if not self.client.next():
                break
            index, balance, btc = self._iteration()

            indices.append(index)
            balances.append(balance)
            btcs.append(btc)
            stocks.append(self.client.current())

        # self._save_graph(indices, [balances, btcs], self.graph_filename, stocks)
        self._save_graph(indices, [balances, btcs], self.graph_filename, None)
        self._save_graph(indices, [btcs], f"BTC_{self.graph_filename}", None)
