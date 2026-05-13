from functools import reduce
from types import TracebackType, UnionType
from typing import Protocol
from abc import ABCMeta, abstractmethod


class ContextManager[T](Protocol, metaclass=ABCMeta):
    @abstractmethod
    def __enter__(self) -> T:
        ...

    @abstractmethod
    def __exit__(self, exc_type: type[BaseException], exc_val: BaseException, exc_tb: TracebackType) -> bool | None:
        ...


def union[T](*types: T) -> UnionType:
    return reduce(lambda a, b: a | b, types)
