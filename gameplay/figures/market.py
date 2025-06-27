from attrs import frozen, define

from gameplay import protocols as proto
from ordered_dict import OrderedDict
from figures_flags import Creatable


class Order(OrderedDict[int, type[proto.Figure]]):
    ...


@define
class FiguresMarket(proto.FiguresMarket):
    _groups: dict[proto.FiguresGroup, Order]

    ...  # important logic here


@define
class FiguresMarketBuilder(proto.FiguresMarketBuilder):
    _groups = dict[proto.FiguresGroup, Order]()

    def register(self, figure: type[proto.Figure], group: proto.FiguresGroup, price: int) -> None:
        assert Creatable in figure.FLAGS

        if group not in self._groups:
            self._groups[group] = Order()

        assert price not in self._groups[group]
        assert figure not in self._groups[group].values()

        self._groups[group][price] = figure

    def build(self) -> proto.FiguresMarket:
        return FiguresMarket(self._groups.copy())


@frozen(eq=False, hash=True)
class FiguresGroup(proto.FiguresGroup):
    def __eq__(self, other: proto.FiguresGroup) -> bool:
        return self is other


BUILDINGS = FiguresGroup()
UNITS = FiguresGroup()
