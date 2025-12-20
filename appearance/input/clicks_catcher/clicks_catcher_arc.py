from typing import Iterable

from attrs import frozen, Factory

from statuses import MISSING, Status
from .click import Click
import appearance.protocols as proto


@frozen
class ClicksCatcher:
    _layers: list[proto.LayerHolder] = Factory(list)

    def update(self, clicks: list[Click]) -> None:
        for click in clicks:
            self.update_from(click)

    def update_from(self, click: Click) -> None:
        layer = self.get_first_layer_that_cat_catch(click)
        layer.catch(click)

    def get_first_layer_that_cat_catch(self, click: Click) -> proto.Layer | Status:
        for layer in self._get_active_layers():
            if layer.can_catch(click):
                return layer
        return MISSING

    def _get_active_layers(self) -> Iterable[proto.Layer]:
        return (layer.layer for layer in self._layers if layer.layer.is_active)
