from attrs import define, field

import core.protocols as proto
from core.resources import ResourcesStockpile


@define
class Player(proto.Player):
    _data: proto.PlayerData
    _inputer: proto.PlayerInputer
    _resources_stockpile: proto.ResourcesStockpile = field(init=False, factory=ResourcesStockpile)

    @property
    def data(self) -> proto.PlayerData:
        return self._data

    @property
    def inputer(self) -> proto.PlayerInputer:
        return self._inputer

    @property
    def resources(self) -> proto.ResourcesStockpile:
        return self._resources_stockpile

    def change_inputer(self, inputer: proto.PlayerInputer) -> None:
        self._inputer = inputer
