from abc import ABCMeta, abstractmethod
from typing import Callable, Protocol

from attrs import define


@define
class OrderedDict[TK, TV](dict[TK, TV]):
    _order: Callable[[tuple[TK, TV]], "SupportsComparison | int | float"] = lambda kv: kv[0]

    def populated_from(self, origin: dict[TK, TV]) -> "OrderedDict[TK, TV]":
        self.update(origin)
        return self

    def ordered(self) -> list[TV]:
        return list(map(lambda item: item[-1], self.ordered_items()))

    def ordered_items(self) -> list[tuple[TK, TV]]:
        return sorted(self.items(), key=self._order)

    def __str__(self) -> str:
        return f'{{\n\t{",\n\t".join(map(lambda kv: f"{kv[0]}: {kv[-1]}", self.ordered_items()))}\n}}'


class SupportsComparison(Protocol, metaclass=ABCMeta):
    @abstractmethod
    def __lt__(self, other: "SupportsComparison") -> bool:
        ...

    @abstractmethod
    def __gt__(self, other: "SupportsComparison") -> bool:
        ...
