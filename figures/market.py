from attrs import frozen, define

import protocols as proto
from ordered_dict import OrderedDict


class Order(OrderedDict[int, type[proto.Figure]]):
    ...


@define
class FiguresMarket(proto.FiguresMarket):
    _kind_to_order: dict[proto.MarketFiguresKind, Order]


@define
class FiguresMarketBuilder(proto.FiguresMarketBuilder):
    _kind_to_order = dict[proto.MarketFiguresKind, Order]()

    def register(self, figure: type[proto.Figure], kind: proto.MarketFiguresKind, price: int) -> None:
        if kind not in self._kind_to_order:
            self._kind_to_order[kind] = Order()

        assert price not in self._kind_to_order[kind]
        assert figure not in self._kind_to_order[kind].values()

        self._kind_to_order[kind][price] = figure

    def build(self) -> proto.FiguresMarket:
        return FiguresMarket(self._kind_to_order.copy())


@frozen
class MarketFiguresKind(proto.MarketFiguresKind):
    ...


BUILDING = MarketFiguresKind()
UNIT = MarketFiguresKind()
