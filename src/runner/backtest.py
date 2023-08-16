import argparse
import pandas as pd

from . import Runner
from src.clients.backtester_client import BacktesterClient
from src.strategies.mae_strategy import MAEStrategy


def main(args):
    data = pd.read_csv(args.filename, index_col=0)
    data.index = pd.to_datetime(data.index)

    runner = Runner(
        context_window=args.context,
        strategy_type=MAEStrategy,
        strategy_args=dict(
            short_period=12,
            long_period=24,
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
    parser.add_argument("-c", "--context", dest="context", type=int, default=120)
    parser.add_argument(
        "-s",
        "--strategy",
        dest="strategy",
        type=str,
        default="mae",
        choices=["mae"],
    )

    args = parser.parse_args()

    main(args)
