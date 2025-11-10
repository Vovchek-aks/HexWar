from attrs import frozen, field

import appearance.protocols as proto
from appearance.input.clicks_catcher import ClicksCatcher
from observer import Event, OnEventSubscriber
from statuses import MISSING


@frozen
class LayersContainerLayer(proto.LayersContainerLayer):
    @classmethod
    def make(cls, layers: list[proto.LayerHolder]) -> "LayersContainerLayer":
        return cls(ClicksCatcher(layers))

    _clicks_catcher: ClicksCatcher
    _was_clicked: Event[proto.Click, None] = field(init=False, factory=Event)

    @property
    def was_clicked(self) -> OnEventSubscriber[proto.Click, None]:
        return self._was_clicked.subscriber

    def can_catch(self, click: proto.Click) -> bool:
        return self._clicks_catcher.get_first_layer_that_cat_catch(click) is not MISSING

    def catch(self, click: proto.Click) -> None:
        assert self.can_catch(click)

        self._was_clicked.invoke(click)
        self._clicks_catcher.update_from(click)
