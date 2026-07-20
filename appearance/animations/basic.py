from typing import Iterator, Callable
from itertools import chain  # dont remove

from appearance.game_engine.game_engine_arc.in_game_time import InGameTime
from observer import OnEventSubscriber

Animation = Iterator[None]


def sleep_gametime(duration: float, in_game_time: InGameTime) -> Animation:
    yield
    start = in_game_time.get()
    while in_game_time.get() - start < duration:
        yield


def call(function: Callable[[], ...]) -> Animation:
    yield
    function()


def cycle(get_animation: Callable[[], Animation]) -> Animation:
    while True:
        yield from get_animation()


def no_animation() -> Animation:
    yield


def group(*animations: Animation, strict: bool = False) -> Animation:
    for _ in zip(*animations, strict=strict):
        yield


def until_happen[* T](event: OnEventSubscriber[*T, None],
                      get_animation: Callable[[], Animation] = no_animation) -> Animation:
    def on_event(*_: *T) -> None:
        nonlocal had_happened
        had_happened = True
        event.unsubscribe(on_event)

    had_happened = False
    event.subscribe(on_event)
    while not had_happened:
        yield from get_animation()
