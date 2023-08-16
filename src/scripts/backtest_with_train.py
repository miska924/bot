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
from src.strategies.claude_strategy import ClaudeStrategy
from src.strategies import Position


logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


INTERVAL = "5m"
DAYS = 365
TRAIN_DAYS = 10
STRATEGY = ClaudeStrategy(30)
# strategy = RandomStrategy()
# strategy = MAEStrategy()
# strategy = MAEStrategy()


def main():
    api_key = os.environ["BINANCE_API_KEY"]
    api_secret = os.environ["BINANCE_SECRET_KEY"]

    binance_client = BinanceClient(
        api_key=api_key, api_secret=api_secret, interval=INTERVAL
    )

    end: dt.datetime = dt.datetime.now()
    start: dt.datetime = end - dt.timedelta(days=DAYS)
    data: pd.DataFrame = binance_client.load(start=start, end=end)
    print(f"start {start}")
    print(end - start)
    print(data.shape)

    for i in range(len(data)):
        print(f"REAL START: {dt.datetime.fromtimestamp(data.iloc[i].time)}")
        break
    train_data: pd.DataFrame = data

    STRATEGY.train(train_data)
    client = BacktesterClient(data, interval=INTERVAL)

    balance = []
    index = []
    for _ in range(30):
        client.next()

    while client.next():
        current_datetime: dt.datetime = client.time()
        ago: dt.datetime = current_datetime - dt.timedelta(days=365)

        data: pd.DataFrame = client.load(start=ago, end=current_datetime)
        action: Position = STRATEGY.action(data)

        if action == Position.LONG:
            client.set_using_part(0.5)
        elif action == Position.SHORT:
            client.set_using_part(-0.5)
        elif action == Position.NONE:
            client.set_using_part(0)
        else:
            pass  # DO NOTHING

        index.append(current_datetime)
        balance.append(client.balance()["sum"])
        # print(client.balance())

    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(10, 5))  # create figure & 1 axis
    ax.plot(index, balance)
    fig.savefig("tmp.png")  # save the figure to file
    plt.close(fig)


if __name__ == "__main__":
    main()
