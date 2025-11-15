from attrs import define

import core.protocols as proto


@define
class Player(proto.Player):
    _data: proto.PlayerData
    _inputer: proto.PlayerInputer

    @property
    def data(self) -> proto.PlayerData:
        return self._data

    @property
    def inputer(self) -> proto.PlayerInputer:
        return self._inputer

    def change_inputer(self, inputer: proto.PlayerInputer) -> None:
        self._inputer = inputer
