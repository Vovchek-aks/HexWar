from attrs import frozen, field

import core.protocols as proto
from core.figures.figures_flags import CanPull, Pullable
from core.protocols import Figure
from observer import Event, OnEventSubscriber


@frozen
class PullingConnections(proto.PullingConnections):
    @classmethod
    def make(cls, figures: proto.Figures) -> "PullingConnections":
        self = cls()
        figures.figure_was_removed.subscribe(lambda figure, _: self._on_figure_deleted(figure))
        figures.figure_was_converted.subscribe(lambda figure, target, _: self._on_figure_was_converted(figure, target))
        return self

    _pullable_of: dict[Figure, Figure] = field(init=False, factory=dict)
    _puller_of: dict[Figure, Figure] = field(init=False, factory=dict)

    _pair_added: Event[Figure, Figure, None] = field(init=False, factory=Event)
    _pair_removed: Event[Figure, Figure, None] = field(init=False, factory=Event)

    @property
    def pair_added(self) -> OnEventSubscriber[Figure, Figure, None]:
        return self._pair_added.subscriber

    @property
    def pair_removed(self) -> OnEventSubscriber[Figure, Figure, None]:
        return self._pair_removed.subscriber

    def register(self, puller: Figure, pullable: Figure) -> None:
        assert CanPull in puller.FLAGS
        assert Pullable in pullable.FLAGS
        assert (puller, pullable) not in self

        self._pullable_of[puller] = pullable
        self._puller_of[pullable] = puller
        self._pair_added.invoke(puller, pullable)

    def unregister(self, puller: Figure, pullable: Figure) -> None:
        assert CanPull in puller.FLAGS
        assert Pullable in pullable.FLAGS
        assert (puller, pullable) in self

        self._pullable_of.pop(puller)
        self._puller_of.pop(pullable)
        self._pair_removed.invoke(puller, pullable)

    def is_puller(self, figure: Figure) -> bool:
        assert CanPull in figure.FLAGS
        return figure in self._pullable_of

    def is_pullable(self, figure: Figure) -> bool:
        assert Pullable in figure.FLAGS
        return figure in self._puller_of

    def get_pullable(self, puller: Figure) -> Figure:
        assert self.is_puller(puller)
        return self._pullable_of[puller]

    def get_puller(self, pullable: Figure) -> Figure:
        assert self.is_pullable(pullable)
        return self._puller_of[pullable]

    def _on_figure_deleted(self, figure: Figure) -> None:
        if CanPull in figure.FLAGS and self.is_puller(figure):
            self.unregister(figure, self._pullable_of[figure])
        if Pullable in figure.FLAGS and self.is_pullable(figure):
            self.unregister(self._puller_of[figure], figure)

    def _on_figure_was_converted(self, figure: Figure, target: Figure) -> None:
        if CanPull not in figure.FLAGS or not self.is_puller(figure):
            return

        pullable = self._pullable_of[figure]
        self.unregister(figure, pullable)
        if CanPull in target.FLAGS:
            self.register(target, pullable)

    def __contains__(self, item: tuple[Figure, Figure]) -> bool:
        puller, pullable = item
        has_puller = puller in self._pullable_of
        has_pullable = pullable in self._puller_of
        if not (has_puller and has_pullable):
            return False

        return (puller is self._puller_of[pullable] and
                pullable is self._pullable_of[puller])
