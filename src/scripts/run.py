import os
import logging
import datetime as dt
import pandas as pd
import time

from src.clients.binance_client import BinanceClient
from src.strategies.random_strategy import RandomStrategy
from src.strategies.manual_strategy import ManualStrategy
from src.strategies import Position


logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


def main():
    api_key = os.environ["BINANCE_API_KEY"]
    api_secret = os.environ["BINANCE_SECRET_KEY"]

    client = BinanceClient(api_key=api_key, api_secret=api_secret, testnet=True)
    strategy = RandomStrategy()


if __name__ == "__main__":
    main()
