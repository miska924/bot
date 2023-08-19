import argparse
import pandas as pd

from . import Runner
from src.clients.backtester_client import BacktesterClient
from src.strategies.macd import MACDStrategy
from src.strategies.nothing import NothingStrategy
from src.strategies.reversals import ReversalsStrategy

from src.indicators.extremum import Max, Min


def main(args):
    data = pd.read_csv(args.filename, index_col=0)
    data.index = pd.to_datetime(data.index)

    runner = Runner(
        context_window=args.context,
        strategy_type=ReversalsStrategy,
        strategy_args=dict(
            indicators=[
                Max(period=100, column="high"),
                Min(period=100, column="low"),
            ],
        ),
        client_type=BacktesterClient,
        client_args=dict(
            data=data,
        ),
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

    args = parser.parse_args()

    main(args)
