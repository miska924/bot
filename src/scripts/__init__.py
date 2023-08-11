import datetime as dt
import pandas as pd
import tqdm
import typing as tp
import matplotlib.pyplot as plt

from src.clients import AbstractClient
from src.strategies import AbstractStrategy, Action


class Runner:
    def __init__(
        self,
        client: AbstractClient,
        strategy: AbstractStrategy,
        window: dt.timedelta,
        graph_filename: str = "tmp.png",
        long: float = 0.5,
        short: float = -0.5,
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
        action: Action = self.strategy.action(data)

        if action == Action.LONG:
            self.client.set_using_part(self.long)
        elif action == Action.SHORT:
            self.client.set_using_part(self.short)
        elif action == Action.NONE:
            self.client.set_using_part(0)
        else:
            pass  # DO NOTHING

        return (
            current_time,
            self.client.balance()["sum"],
            self.client.balance()["BTC"],
        )

    @staticmethod
    def _save_graph(
        indices: tp.List[dt.datetime], values: tp.List[float], filename: str
    ):
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(20, 5))
        fig.autofmt_xdate(rotation=45)
        ax.plot(indices, values)
        fig.savefig(filename)
        plt.close(fig)

    def run(self):
        indices = []
        balances = []
        btcs = []

        for _ in tqdm.tqdm(range(self.client.data.shape[0])):
            if not self.client.next():
                break
            index, balance, btc = self._iteration()

            indices.append(index)
            balances.append(balance)
            btcs.append(btc)

        self._save_graph(indices, balances, self.graph_filename)
        self._save_graph(indices, btcs, f"BTC_{self.graph_filename}")
