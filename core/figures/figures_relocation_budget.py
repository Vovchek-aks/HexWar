from attrs import frozen, Factory

import core.protocols as proto


@frozen
class FiguresRelocationBudget(proto.FiguresRelocationBudget):
    _figures_bills: dict[proto.Figure, int] = Factory(dict)

    @property
    def figures_bills(self) -> dict[proto.Figure, int]:
        return dict(self._figures_bills)

    def clear(self) -> None:
        self._figures_bills.clear()

    def pop(self, figure: proto.Figure) -> int:
        return self._figures_bills.pop(figure) if figure in self._figures_bills else 0

    def of(self, figure: proto.Figure) -> int:
        return self._figures_bills.get(figure, 0)

    def can_spend(self, figure: proto.Figure, pay_count: int) -> bool:
        return self.of(figure) + pay_count <= figure.MOVES_BUDGET

    def add(self, figure: proto.Figure, pay_count: int) -> None:
        assert self.can_spend(figure, pay_count)

        if figure not in self._figures_bills:
            self._figures_bills[figure] = 0

        self._figures_bills[figure] += pay_count
