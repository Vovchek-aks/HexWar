from attrs import define


@define
class ListChanger[T]:
    _values: list[T]
    _index: int = 0

    @property
    def value(self) -> T:
        return self._values[self._index]

    def set(self, value: T) -> None:
        assert value in self._values
        self._index = self._values.index(value)

    def next(self) -> None:
        self._index = (self._index + 1) % len(self._values)

    def back(self) -> None:
        self._index = (self._index - 1) % len(self._values)
