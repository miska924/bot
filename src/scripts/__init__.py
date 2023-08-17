import datetime as dt
import pandas as pd
import typing as tp
import matplotlib.pyplot as plt
import matplotlib as mpl
import time

from src.clients import AbstractClient
from src.strategies import AbstractStrategy, Position

import matplotlib.pyplot as plt
import mplfinance as mpf
import matplotlib.animation as animation


def add_row(data: pd.DataFrame, index, row: dict):
    if data is None:
        tmp = pd.DataFrame(
            [row],
        )
        tmp.index = (index,)
        return tmp

    data.loc[index] = row
    return data


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
        context_window: int,
        client_type: type,
        strategy_type: type,
        client_args: dict = dict(),
        strategy_args: dict = dict(),
        long: float = 0.9,
        short: float = -0.9,
        animate: bool = True,
    ):
        self.context_window = context_window
        self.client: AbstractClient = client_type(**client_args)
        self.strategy: AbstractStrategy = strategy_type(**strategy_args)

        self.long: float = long
        self.short: float = short
        self.animate: bool = animate

        self.balance: pd.DataFrame = None

        self.long_positions: pd.DataFrame = None
        self.short_positions: pd.DataFrame = None
        self.zero_positions: pd.DataFrame = None

        self._iterate_time = 0
        self._render_time = 0

    def _update_balance(self):
        balance = self.client.balance()
        self.balance = add_row(
            data=self.balance,
            index=self.client.time(),
            row=dict(
                balance=balance["sum"],
                using=balance[self.client.get_using()],
            ),
        )

    def _iterate(self):
        data: pd.DataFrame = self.client.last(self.context_window)
        action: Position = self.strategy.action(data, self.client.position())

        if action == Position.LONG:
            self.client.set_using_part(self.long)
            self.long_positions = add_row(
                data=self.long_positions,
                index=self.client.time(),
                row=dict(value=self.client.price()),
            )

        if action == Position.SHORT:
            self.client.set_using_part(self.short)
            self.short_positions = add_row(
                data=self.short_positions,
                index=self.client.time(),
                row=dict(value=self.client.price()),
            )

        if action == Position.NONE:
            self.client.set_using_part(0)
            self.zero_positions = add_row(
                data=self.zero_positions,
                index=self.client.time(),
                row=dict(value=self.client.price()),
            )

    def run(self):
        fig = mpf.figure(figsize=(10, 10))
        ax1, ax2, ax3 = fig.subplots(
            nrows=3,
            ncols=1,
            gridspec_kw={"height_ratios": [1, 1, 4]},
            sharex=True,
        )

        def animate(ival, self, ax1, ax2, ax3):
            self.last = time.time()
            for i in range(10):
                self.client.next()
                self._iterate()
                self._update_balance()

            context = self.client.last(self.context_window)

            self._iterate_time += time.time() - self.last

            self.last = time.time()

            ax1.clear()
            ax2.clear()
            ax3.clear()

            mpf.plot(
                context,
                ax=ax3,
                style="yahoo",
                type="candle",
                show_nontrading=True,
            )

            for positions, marker, color in [
                (self.short_positions, "v", "black"),
                (self.long_positions, "^", "black"),
                (self.zero_positions, "o", "gray"),
            ]:
                if positions is None:
                    continue
                context_positions = positions[positions.index >= context.index[0]]
                ax3.scatter(
                    context_positions.index,
                    context_positions.value,
                    marker=marker,
                    color=color,
                    s=100,
                )

            context_balance = self.balance[self.balance.index >= context.index[0]]
            ax1.plot(
                context_balance.index,
                context_balance.balance,
            )
            ax2.plot(
                context_balance.index,
                context_balance.using,
            )
            self._render_time += time.time() - self.last
            print(f"render: {self._render_time}")
            print(f"iterate: {self._iterate_time}")

        ani = animation.FuncAnimation(
            fig, animate, fargs=(self, ax1, ax2, ax3), interval=100
        )
        mpf.show()
