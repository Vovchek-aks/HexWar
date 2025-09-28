from typing import Iterable

import pygame as pg
from attrs import frozen, define

from statuses import Status, MISSING


@frozen
class Events:
    _events: list[pg.event.Event]

    def select(self, target: int) -> list[pg.event.Event] | Status:
        events = list(filter(lambda event: event.type == target, self._events))
        if events:
            return events

        return MISSING

    def get(self, target: int) -> pg.event.Event | Status:
        events = self.select(target)
        if events is MISSING:
            return MISSING

        return events[0]

    def __contains__(self, item: int) -> bool:
        return self.get(item) is not MISSING

    def __iter__(self) -> Iterable[pg.event.Event]:
        return iter(self._events)


@define
class UpdatableEvents:
    @classmethod
    def new(cls) -> "UpdatableEvents":
        events = cls(Events([]))
        events.read()
        return events

    _events: Events

    def get(self) -> Events:
        return self._events

    def read(self) -> None:
        self._events = Events(pg.event.get())
