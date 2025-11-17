from attrs import frozen, Factory

import core.protocols as proto


@frozen
class FiguresRelocationBudget(proto.FiguresRelocationBudget):
    figures_bills: dict[proto.Figure, int] = Factory(dict)

    def clear(self) -> None:
        self.figures_bills.clear()

    def of(self, figure: proto.Figure) -> int:
        return self.figures_bills.get(figure, 0)

    def can_spend(self, figure: proto.Figure, pay_count: int) -> bool:
        return self.of(figure) + pay_count <= figure.MOVES_BUDGET

    def add(self, figure: proto.Figure, pay_count: int) -> None:
        assert self.can_spend(figure, pay_count)

        if figure not in self.figures_bills:
            self.figures_bills[figure] = 0

        self.figures_bills[figure] += pay_count
