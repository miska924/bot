import os
import logging
import datetime as dt
import pandas as pd
import time

from src.clients.binance_client import BinanceClient
from src.strategies.random_strategy import RandomStrategy
from src.strategies.manual_strategy import ManualStrategy
from src.strategies import Action


logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


def main():
    api_key = os.environ["BINANCE_API_KEY"]
    api_secret = os.environ["BINANCE_SECRET_KEY"]

    client = BinanceClient(api_key=api_key, api_secret=api_secret, testnet=True)
    strategy = RandomStrategy()

    try:
        while True:
            current_datetime: dt.datetime = dt.datetime.now()
            hour_ago: dt.datetime = current_datetime - dt.timedelta(hours=1)

            data: pd.DataFrame = client.load(start=hour_ago, end=current_datetime)
            action: Action = strategy.action(data)

            if action == Action.LONG:
                client.set_using_part(0.5)
            elif action == Action.SHORT:
                client.set_using_part(0)
            elif action == Action.NONE:
                client.set_using_part(0)

            logging.info(client.balance())
            # time.sleep(1)

    except Exception as e:
        logging.error(e)
        client.set_using_part(0)


if __name__ == "__main__":
    main()
