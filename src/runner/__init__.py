import datetime as dt
import pandas as pd
import tqdm
import time
import typing as tp
import matplotlib.pyplot as plt
import matplotlib as mpl

from src.clients import AbstractClient
from src.strategies import AbstractStrategy, Position

import tqdm
import matplotlib.pyplot as plt
import mplfinance as mpf
import matplotlib.animation as animation


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

    def _update_balance(self):
        balance = self.client.balance()
        tmp = pd.DataFrame(
            [
                dict(
                    balance=balance["sum"],
                    using=balance[self.client.get_using()],
                )
            ],
        )
        tmp.index = (self.client.time(),)

        self.balance = (
            pd.concat(
                [self.balance, tmp],
            )
            if self.balance is not None
            else tmp
        )

    def _iterate(self):
        data: pd.DataFrame = self.client.last(self.context_window)
        action: Position = self.strategy.action(data, self.client.position())

        if action == Position.LONG:
            self.client.set_using_part(self.long)

        if action == Position.SHORT:
            self.client.set_using_part(self.short)

        if action == Position.NONE:
            self.client.set_using_part(0)

        if action is not None:
            print(action)

    def run(self):
        fig = mpf.figure(figsize=(10, 10))
        ax1, ax2, ax3 = fig.subplots(
            nrows=3,
            ncols=1,
            gridspec_kw={"height_ratios": [1, 1, 4]},
            sharex=True,
        )

        def animate(ival):
            self._iterate()
            self._update_balance()

            ax1.clear()
            ax2.clear()
            ax3.clear()
            context = self.client.last(self.context_window)
            mpf.plot(
                context,
                ax=ax3,
                style="yahoo",
                type="candle",
                show_nontrading=True,
            )
            # print(self.balance.index)
            context_balance = self.balance[self.balance.index >= context.index[0]]
            ax1.plot(
                context_balance.index,
                context_balance.balance,
                label="balance",
            )
            ax2.plot(
                context_balance.index,
                context_balance.using,
                label=self.client.get_using(),
            )

            self.client.next()

        ani = animation.FuncAnimation(fig, animate, interval=1)
        mpf.show()
