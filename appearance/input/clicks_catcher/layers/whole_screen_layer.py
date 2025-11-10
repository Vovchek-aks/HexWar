from attrs import frozen, field

import appearance.protocols as proto
from observer import Event, OnEventSubscriber


@frozen
class WholeScreenLayer(proto.WholeScreenLayer):
    _was_clicked: Event[proto.Click, None] = field(init=False, factory=Event)

    @property
    def was_clicked(self) -> OnEventSubscriber[proto.Click, None]:
        return self._was_clicked.subscriber

    def can_catch(self, click: proto.Click) -> bool:
        return True

    def catch(self, click: proto.Click) -> None:
        assert self.can_catch(click)

        self._was_clicked.invoke(click)
