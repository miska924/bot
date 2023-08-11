import os
import logging
import datetime as dt
import pandas as pd
import time
from matplotlib import pyplot as plt

from src.clients.binance_client import BinanceClient
from src.clients.backtester_client import BacktesterClient
from src.strategies.random_strategy import RandomStrategy
from src.strategies.manual_strategy import ManualStrategy
from src.strategies.mae_strategy import MAEStrategy
from src.strategies import Action


logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


INTERVAL = "30m"
DAYS = 30
STRATEGY = MAEStrategy(0)
# strategy = RandomStrategy()
# strategy = MAEStrategy()
# strategy = MAEStrategy()


def main():
    api_key = os.environ["BINANCE_API_KEY"]
    api_secret = os.environ["BINANCE_SECRET_KEY"]

    binance_client = BinanceClient(
        api_key=api_key, api_secret=api_secret, interval=INTERVAL, testnet=True
    )

    end: dt.datetime = dt.datetime.now()
    start: dt.datetime = end - dt.timedelta(days=DAYS)

    data = binance_client.load(start=start, end=end)
    logging.info(f"DATA SHAPE {data.shape}")
    client = BacktesterClient(data, interval=INTERVAL)

    balance = []
    index = []
    while client.next():
        current_datetime: dt.datetime = client.time()
        ago: dt.datetime = current_datetime - dt.timedelta(hours=24)

        data: pd.DataFrame = client.load(start=ago, end=current_datetime)
        action: Action = STRATEGY.action(data)

        if action == Action.LONG:
            client.set_using_part(0.5)
        elif action == Action.SHORT:
            client.set_using_part(-0.5)
        elif action == Action.NONE:
            client.set_using_part(0)
        else:
            pass  # DO NOTHING

        index.append(current_datetime)
        balance.append(client.balance()["sum"])

    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(10, 5))  # create figure & 1 axis
    ax.plot(index, balance)
    fig.savefig("tmp.png")  # save the figure to file
    plt.close(fig)


if __name__ == "__main__":
    main()
