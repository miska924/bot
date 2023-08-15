import os
import logging
import datetime as dt
import pandas as pd
import time
import tqdm
import matplotlib.pyplot as plt
import mplfinance as mpf
import matplotlib.animation as animation

from src.clients.binance_client import BinanceClient
from src.clients.backtester_client import BacktesterClient
from src.strategies import Combination
from src.strategies.random_strategy import RandomStrategy
from src.strategies.manual_strategy import ManualStrategy
from src.strategies.mae_strategy import MAEStrategy
from src.strategies.reversals_strategy import ReversalsStrategy
from src.strategies.reversals_v2_strategy import ReversalsV2Strategy
from . import Runner, save_plot


logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


INTERVAL_MINUTES = 15
INTERVAL = f"{INTERVAL_MINUTES}m"

WINDOW_SIZE = 120

HOURS = 24 * 30 * 12
STEP = 24 * 30
# strategy = RandomStrategy()
# strategy = MAEStrategy()
# strategy = MAEStrategy()

USE_CACHE = True
SAVE = True


def main():
    # data = pd.read_csv("data.csv", index_col=0)

    # data.index = [
    #     dt.datetime.fromtimestamp(item * 1000) for item in data.index.to_list()
    # ]

    api_key = os.environ["BINANCE_API_KEY"]
    api_secret = os.environ["BINANCE_SECRET_KEY"]
    # logging.info(api_key)
    # logging.info(api_secret)

    client = BinanceClient(
        api_key=api_key, api_secret=api_secret, interval="5m", testnet=False
    )

    fig = mpf.figure(figsize=(7, 8))
    ax1 = fig.add_subplot(1, 1, 1)

    def animate(ival):
        ax1.clear()
        client.next()
        mpf.plot(
            client.last(20),
            ax=ax1,
            style="yahoo",
            type="candle",
        )

    ani = animation.FuncAnimation(fig, animate, interval=100)
    mpf.show()
    time.sleep(1)

    # save_plot(
    #     indices=[dt.datetime.fromtimestamp(t) for t in data.time],
    #     values=[data.high, data.low, data.close, data.open],
    #     filename="BTC.png",
    # )
    # print(data.shape)
    # # print(exact_data.shape)
    # # logging.info(f"DATA SHAPE {data.shape}")

    # for strategy in [
    #     # Combination((ReversalsStrategy(), MAEStrategy())),
    #     ReversalsV2Strategy(),
    #     # ReversalsStrategy(),
    #     # MAEStrategy(),
    #     # RandomStrategy(),
    # ]:
    #     client = BacktesterClient(data, interval=INTERVAL)
    #     Runner(
    #         client=client,
    #         strategy=strategy,
    #         window=dt.timedelta(minutes=INTERVAL_MINUTES * WINDOW_SIZE),
    #         graph_filename=f"{strategy.__class__.__name__}.png",
    #     ).run()


if __name__ == "__main__":
    main()
