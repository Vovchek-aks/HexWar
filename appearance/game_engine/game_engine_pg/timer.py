from attrs import define
import pygame as pg

ONE_SECOND = 1_000


@define
class Timer:
    @classmethod
    def make(cls, ups: int) -> "Timer":
        clock = pg.time.Clock()
        dt = 1 / ups
        return cls(ups, dt, clock)

    _ups: int
    _dt: float
    _clock: pg.time.Clock

    @property
    def dt(self) -> float:
        return self._dt

    def tick(self) -> None:
        self._dt = self._clock.tick(self._ups) / ONE_SECOND
