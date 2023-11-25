import logging
import datetime as dt
import pandas as pd
import tqdm
import argparse

from src.clients.binance_client import BinanceClient


logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


STEP = 1000


def main(args):
    assert args.window > 0

    client = BinanceClient(
        api_key=args.token,
        api_secret=args.secret,
        interval=args.interval,
        testnet=False,
    )

    current: dt.datetime = client.time()
    frames = []
    for i in tqdm.tqdm(range((args.window + STEP - 1) // STEP)):
        begin = i * STEP
        end = min(args.window, (i + 1) * STEP)

        frame = client.last(end - begin, offset=args.window - end, time=current)
        frames.append(frame)

    data: pd.DataFrame = pd.concat(frames)

    data.to_csv(args.filename)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Load",
        description="Loads historical candles",
    )

    parser.add_argument(
        "-f", "--filename", dest="filename", type=str, default="data.csv"
    )
    parser.add_argument("-w", "--window", dest="window", type=int, default=1000)
    parser.add_argument(
        "-i",
        "--interval",
        dest="interval",
        type=str,
        default="15m",
        choices=["15m", "1h", "30m", "1s", "1d", "1m"],
    )

    parser.add_argument("-t", "--token", dest="token", type=str, required=True)
    parser.add_argument("-s", "--secret", dest="secret", type=str, required=True)

    args = parser.parse_args()

    main(args)
