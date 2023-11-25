from .abstract import AbstractClient


class BacktestClient(AbstractClient):
    def __init__(self) -> None:
        pass

    def long(self) -> None:
        raise NotImplementedError()

    def short(self) -> None:
        raise NotImplementedError()

    def close(self) -> None:
        raise NotImplementedError()

    def balance(self) -> None:
        raise NotImplementedError()
