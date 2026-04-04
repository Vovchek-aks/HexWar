from attrs import define


@define
class FloatChanger:
    _value: float
    _min: float
    _max: float
    _step: float = 0.1
    _precision_power: int = 1

    @property
    def value(self) -> float:
        return self._value

    def set(self, value: float) -> None:
        self._value = value
        self._fix()

    def next(self) -> None:
        self._value += self._step
        self._fix()

    def back(self) -> None:
        self._value -= self._step
        self._fix()

    def _fix(self) -> None:
        self._value = round(max(self._min, min(self._max, self._value)), self._precision_power)
