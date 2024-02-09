from . import AbstractClient

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException

import logging
import datetime as dt
import pandas as pd
import math
from pytimeparse.timeparse import timeparse
import requests
import os
import json


def telegram_bot_sendtext(bot_message):
   bot_token = os.getenv('TRADE_NOTIFIER_TOKEN')
   bot_chatID = os.getenv('TRADE_NOTIFIER_CHAT_ID')
   send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message

   response = requests.get(send_text)

   return response.json()


class BinanceClient(AbstractClient):
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        target: str = "USDT",
        using: str = "BTC",
        interval: str = "15m",
        testnet: bool = True,
    ):
        self.using = using
        self.target = target
        self.symbol = f"{using}{target}"
        self.interval = interval
        self.api_key = api_key
        self.api_secret = api_secret
        self.client = Client(api_key, api_secret, testnet=testnet)

        symbol_info = self.client.get_symbol_info(self.symbol)
        # logging.info(symbol_info)
        self.min_qty = float(symbol_info["filters"][1]["minQty"])
        self.precision = symbol_info["baseAssetPrecision"]
        self.min_notional = float(symbol_info["filters"][6]["minNotional"])
        self.max_notional = float(symbol_info["filters"][6]["maxNotional"])
        # self.max_leverage = self.client.get_max_margin_loan(asset=self.using)
        # logging.info(self.max_leverage)
        telegram_bot_sendtext("Started")

    def last(self, count: int, offset: int = 0, time: dt.datetime = None):
        window_timedelta = dt.timedelta(seconds=timeparse(self.interval)) * (count + 1)
        offset_timedelta = dt.timedelta(seconds=timeparse(self.interval)) * (offset)
        end = (self.time() if not time else time) - offset_timedelta
        start = end - window_timedelta
        res = self.load(start, end)
        res = res.tail(count)
        return res

    def load(self, start: dt.datetime, end: dt.datetime) -> pd.DataFrame:
        try:
            start_str: str = start.strftime("%Y-%m-%d %H:%M:%S")
            end_str: str = end.strftime("%Y-%m-%d %H:%M:%S")
            bars = self.client.get_historical_klines(
                self.symbol,
                self.interval,
                start_str,
                end_str,
            )
            # logging.info(start_str)
            # logging.info(end_str)
            # logging.info(bars)
        except BinanceAPIException as e:
            logging.error(f"Ошибка получения данных: {e}")
            return None

        data = []
        for b in bars:
            bar = {
                "time": b[0] / 1000,
                "open": float(b[1]),
                "high": float(b[2]),
                "low": float(b[3]),
                "close": float(b[4]),
                "volume": float(b[5]),
            }
            data.append(bar)

        data = pd.DataFrame(data)
        data.index = [dt.datetime.fromtimestamp(item) for item in data.time.to_list()]

        return data

    def _order(self, quantity: float) -> None:
        # print(quantity)
        try:
            if quantity < 0:
                order = self.client.order_market_sell(
                    symbol=self.symbol,
                    quantity=f"{-quantity:0.{self.precision}f}",
                )
            elif quantity > 0:
                order = self.client.order_market_buy(
                    symbol=self.symbol,
                    quantity=f"{quantity:0.{self.precision}f}",
                )
            telegram_bot_sendtext(json.dumps(self.balance(), indent=2))
        except BinanceAPIException as e:
            error = f"Ошибка при открытии позиции: {e}"
            logging.error(error)
            telegram_bot_sendtext(error)

        except BinanceOrderException as e:
            error = f"Ошибка создания ордера: {e}"
            logging.error(error)
            telegram_bot_sendtext(error)

    def price(self):
        try:
            price = self.client.get_symbol_ticker(symbol=self.symbol)
            return float(price["price"])

        except BinanceAPIException as e:
            logging.error(f"Ошибка получения цены: {e}")
            return None

    def asset_balance(self, asset: str) -> float:
        try:
            amount = self.client.get_asset_balance(asset=asset)
            return float(amount["free"])

        except (TypeError, KeyError, BinanceAPIException) as e:
            logging.error(f"Ошибка получения баланса: {e}")
            return None
