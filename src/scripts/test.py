import argparse
import pandas as pd

from . import Runner
from src.clients.binance_client import BinanceClient
from src.strategies.macd import MACDStrategy
from src.strategies.nothing import NothingStrategy
from src.strategies.reversals import ReversalsStrategy
from src.strategies.support_resistance import SupportResistance
from src.strategies.aleks5d_stupid_2 import Aleks5dStupid2

from src.indicators.extremum import Max, Min
from src.indicators.optimum import Support, Resistance
from src.indicators.imbalance import Imbalance
from src.indicators.trend import Trend
from src.indicators.liquidity import Liquidity
from src.indicators.candlestick import Hammer


def main(args):
    runner = Runner(
        context_window=args.context,
        strategy_type=Aleks5dStupid2,
        strategy_args=dict(),
        client_type=BinanceClient,
        client_args=dict(
            api_key=args.token,
            api_secret=args.secret,
            testnet=False,
            interval="1m",
        ),
        animate=args.animate,
    )
    runner.run()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Run",
        description="Run strategy",
    )

    parser.add_argument("-c", "--context", dest="context", type=int, default=200)
    parser.add_argument("-a", "--animate", dest="animate", action="store_true")

    parser.add_argument("-t", "--token", dest="token", type=str, required=True)
    parser.add_argument("-s", "--secret", dest="secret", type=str, required=True)

    args = parser.parse_args()

    main(args)
