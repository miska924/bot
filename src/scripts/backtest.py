import os
import logging
import datetime as dt
import pandas as pd
import time
import tqdm
import matplotlib.pyplot as plt

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
    if not USE_CACHE:
        api_key = os.environ["BINANCE_API_KEY"]
        api_secret = os.environ["BINANCE_SECRET_KEY"]
        # logging.info(api_key)
        # logging.info(api_secret)

        binance_client = BinanceClient(
            api_key=api_key, api_secret=api_secret, interval="15m", testnet=False
        )

        binance_client_exact = BinanceClient(
            api_key=api_key, api_secret=api_secret, interval="1s", testnet=False
        )

        current: dt.datetime = dt.datetime.now()
        # current = dt.datetime(year=2022, month=7, day=28)
        frames = []
        # exact_frames = []
        for i in tqdm.tqdm(range(0, HOURS, STEP)):
            start: dt.datetime = current - dt.timedelta(hours=HOURS - i)
            end: dt.datetime = current - dt.timedelta(hours=HOURS - i - STEP)
            frame = binance_client.load(start=start, end=end)
            # exact_frame = binance_client_exact.load(start=start, end=end)
            # logging.info(f"FRAME SHAPE {frame.shape}")
            frames.append(frame)
            # exact_frames.append(exact_frame)

        data = pd.concat(frames)
        # exact_data = pd.concat(exact_frames)
        if SAVE:
            data.to_csv("data.csv")
            # exact_data.to_csv("exact_data.csv")
    else:
        data = pd.read_csv("data.csv")
        # exact_data = pd.read_csv("exact_data.csv")

    # print(data.time.to_list())
    save_plot(
        indices=[dt.datetime.fromtimestamp(t) for t in data.time],
        values=[data.high, data.low, data.close, data.open],
        filename="BTC.png",
    )
    print(data.shape)
    # print(exact_data.shape)
    # logging.info(f"DATA SHAPE {data.shape}")

    for strategy in [
        # Combination((ReversalsStrategy(), MAEStrategy())),
        ReversalsV2Strategy(),
        # ReversalsStrategy(),
        # MAEStrategy(),
        # RandomStrategy(),
    ]:
        client = BacktesterClient(data, interval=INTERVAL)
        Runner(
            client=client,
            strategy=strategy,
            window=dt.timedelta(minutes=INTERVAL_MINUTES * WINDOW_SIZE),
            graph_filename=f"{strategy.__class__.__name__}.png",
        ).run()


if __name__ == "__main__":
    main()
