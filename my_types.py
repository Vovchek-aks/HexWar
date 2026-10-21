from functools import reduce
from types import TracebackType, UnionType
from typing import Protocol, Callable
from abc import ABCMeta, abstractmethod


class ContextManager[T](Protocol, metaclass=ABCMeta):
    @abstractmethod
    def __enter__(self) -> T:
        ...

    @abstractmethod
    def __exit__(self, exc_type: type[BaseException], exc_val: BaseException, exc_tb: TracebackType) -> bool | None:
        ...


def union[T: type](*types: T) -> UnionType:
    return reduce(lambda a, b: a | b, types)


def combine(*functions: Callable[[], None]) -> Callable[[], None]:
    def do() -> None:
        for function in functions:
            function()

    return do


def call(function: Callable[[], None]) -> None:
    function()
