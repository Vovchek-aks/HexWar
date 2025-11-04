from attrs import frozen, field

import appearance.protocols as proto
from appearance.protocols import Click
from observer import Event, OnEventSubscriber


@frozen
class WholeScreenLayer(proto.WholeScreenLayer):
    _click_happened: Event[Click, None] = field(init=False, factory=Event)

    @property
    def click_happened(self) -> OnEventSubscriber[Click, None]:
        return self._click_happened.subscriber

    def can_catch(self, click: proto.Click) -> bool:
        return True

    def catch(self, click: proto.Click) -> None:
        self._click_happened.invoke(click)
