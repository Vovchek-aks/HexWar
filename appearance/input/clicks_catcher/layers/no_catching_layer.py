from attrs import frozen, field

import appearance.protocols as proto
from observer import Event, OnEventSubscriber


@frozen
class NoCatchingLayer(proto.ClicksCatchingLayer):
    _was_clicked: Event[proto.Click, None] = field(init=False, factory=Event)

    @property
    def was_clicked(self) -> OnEventSubscriber[proto.Click, None]:
        return self._was_clicked.subscriber


    def can_catch(self, click: proto.Click) -> bool:
        return False

    def catch(self, click: proto.Click) -> None:
        assert self.can_catch(click)
