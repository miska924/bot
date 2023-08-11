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
from . import Runner


logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


INTERVAL_MINUTES = 1
INTERVAL = f"{INTERVAL_MINUTES}m"

WINDOW_SIZE = 30

DAYS = 365
STEP = 30
# strategy = RandomStrategy()
# strategy = MAEStrategy()
# strategy = MAEStrategy()


def main():
    api_key = os.environ["BINANCE_API_KEY"]
    api_secret = os.environ["BINANCE_SECRET_KEY"]
    # logging.info(api_key)
    # logging.info(api_secret)

    binance_client = BinanceClient(
        api_key=api_key, api_secret=api_secret, interval=INTERVAL, testnet=False
    )

    current: dt.datetime = dt.datetime.now()
    frames = []
    for i in tqdm.tqdm(range(0, DAYS, STEP)):
        start: dt.datetime = current - dt.timedelta(days=DAYS - i)
        end: dt.datetime = current - dt.timedelta(days=DAYS - i - STEP)
        frame = binance_client.load(start=start, end=end)
        # logging.info(f"FRAME SHAPE {frame.shape}")
        frames.append(frame)

    data = pd.concat(frames)
    Runner._save_graph(indices=data.time, values=data.close, filename="BTC.png")
    print(data.shape)
    # logging.info(f"DATA SHAPE {data.shape}")

    for strategy in [
        Combination((ReversalsStrategy(), MAEStrategy())),
        ReversalsStrategy(),
        MAEStrategy(),
        RandomStrategy(),
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
