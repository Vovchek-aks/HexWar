from attrs import define


@define
class IntChanger:
    _value: int
    _min: int
    _max: int
    _step: int = 1

    @property
    def value(self) -> int:
        return self._value

    def set(self, value: int) -> None:
        self._value = value
        self._fix()

    def next(self) -> None:
        self._value += self._step
        self._fix()

    def back(self) -> None:
        self._value -= self._step
        self._fix()

    def _fix(self) -> None:
        self._value = max(self._min, min(self._max, self._value))
