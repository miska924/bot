import argparse
import pandas as pd

from . import Runner
from src.clients.backtester_client import BacktesterClient
from src.strategies.macd import MACDStrategy
from src.strategies.nothing import NothingStrategy
from src.strategies.reversals import ReversalsStrategy
from src.strategies.support_resistance import SupportResistance

from src.indicators.extremum import Max, Min
from src.indicators.optimum import Support, Resistance


def main(args):
    data = pd.read_csv(args.filename, index_col=0)
    data.index = pd.to_datetime(data.index)

    runner = Runner(
        context_window=args.context,
        strategy_type=SupportResistance,
        strategy_args=dict(),
        client_type=BacktesterClient,
        client_args=dict(
            data=data,
        ),
        animate=args.animate,
    )

    runner.run()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="BackTest",
        description="Test strategy using historical data",
    )

    parser.add_argument(
        "-f", "--filename", dest="filename", type=str, default="data.csv"
    )
    parser.add_argument("-c", "--context", dest="context", type=int, default=200)
    parser.add_argument(
        "-s",
        "--strategy",
        dest="strategy",
        type=str,
        default="macd",
        choices=["macd", "nothing"],
    )
    parser.add_argument("-a", "--animate", dest="animate", action="store_true")

    args = parser.parse_args()

    main(args)
