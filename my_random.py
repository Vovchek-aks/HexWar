import random
from contextlib import contextmanager
from typing import Iterator


@contextmanager
def temporarily_seed(seed: ...) -> Iterator[None]:
    state = random.getstate()
    random.seed(str(seed))
    yield
    random.setstate(state)
