from types import TracebackType
from typing import Protocol
from abc import ABCMeta, abstractmethod


class ContextManager[T](Protocol, metaclass=ABCMeta):
    @abstractmethod
    def __enter__(self) -> T:
        ...

    @abstractmethod
    def __exit__(self, exc_type: type[BaseException], exc_val: BaseException, exc_tb: TracebackType) -> bool | None:
        ...
