from attrs import define


@define
class InGameTime:
    _time: float = 0

    def get(self) -> float:
        return self._time

    def update(self, dt: float) -> None:
        self._time += dt
