from functools import wraps
from types import TracebackType
from typing import Callable
from time import perf_counter as time

from attrs import define


def time_it[T: Callable](function: T) -> T:
    @wraps(function)
    def wrapper(*args, **kwargs):
        name = function.__name__
        print(f"{name} ======= STARTED =======")
        start = time()
        result = function(*args, **kwargs)
        print(f"{name}: {time() - start}")
        print(f"{name} ======== ENDED ========")
        print()
        return result

    return wrapper


@define
class Timer:
    _start: float = 0

    def __enter__(self) -> "Timer":
        self._start = time()
        return self

    def __exit__(self, exc_type: type[BaseException], exc_val: BaseException, exc_tb: TracebackType) -> bool | None:
        print(time() - self._start)
        return None
