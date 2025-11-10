from attrs import frozen

import appearance.protocols as proto
from appearance.input.clicks_catcher import ClicksCatcher
from statuses import MISSING


@frozen
class LayersContainerLayer(proto.LayersContainerLayer):
    @classmethod
    def make(cls, layers: list[proto.LayerHolder]) -> "LayersContainerLayer":
        return cls(ClicksCatcher(layers))

    _clicks_catcher: ClicksCatcher

    def can_catch(self, click: proto.Click) -> bool:
        return self._clicks_catcher.get_first_layer_that_cat_catch(click) is not MISSING

    def catch(self, click: proto.Click) -> None:
        self._clicks_catcher.update_from(click)
