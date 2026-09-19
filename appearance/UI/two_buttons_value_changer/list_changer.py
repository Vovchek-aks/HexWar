from attrs import define


@define
class ListChanger[T]:
    _values: list[T]
    _index: int = 0

    @property
    def values(self) -> list[T]:
        return list(self._values)

    @property
    def value(self) -> T:
        return self._values[self._index]

    def set(self, value: T) -> None:
        assert value in self._values
        self._index = self._values.index(value)

    def insert(self, index: int, value: T) -> None:
        current = self.value
        self._values.insert(index, value)
        self._index = self._values.index(current)

    def next(self) -> None:
        self._index = (self._index + 1) % len(self._values)

    def back(self) -> None:
        self._index = (self._index - 1) % len(self._values)
