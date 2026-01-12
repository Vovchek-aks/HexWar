from attrs import define, field

import core.protocols as proto
from core.player.inputers.bot_player_inputer import BotPlayerInputer
from core.resources import ResourcesStockpile


@define(eq=True, hash=True)
class Player(proto.Player):
    _data: proto.PlayerData = field(eq=False, hash=False)
    _inputer: proto.PlayerInputer = field(eq=False, hash=False)

    _resources_stockpile: proto.ResourcesStockpile = field(init=False, factory=ResourcesStockpile, eq=False, hash=False)
    _id: int = field(init=False)

    def __attrs_post_init__(self) -> None:
        self._id = id(self)

    @property
    def data(self) -> proto.PlayerData:
        return self._data

    @property
    def inputer(self) -> proto.PlayerInputer:
        return self._inputer

    @property
    def need_ui(self) -> bool:
        return not isinstance(self.inputer, BotPlayerInputer)

    @property
    def resources(self) -> proto.ResourcesStockpile:
        return self._resources_stockpile

    def change_inputer(self, inputer: proto.PlayerInputer) -> None:
        self._inputer = inputer
