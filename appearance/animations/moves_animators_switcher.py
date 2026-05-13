from attrs import define

import appearance.protocols as proto
from core.player.inputers.bot_player_inputer import BotPlayerInputer
from core.protocols import Master, Player


@define
class MovesAnimatorsSwitcher:
    @classmethod
    def make(cls,
             master: Master,
             players_moves_animator: proto.MovesAnimator,
             bots_moves_animator: proto.MovesAnimator) -> "MovesAnimatorsSwitcher":
        self = cls(players_moves_animator, bots_moves_animator, players_moves_animator)
        master.turn_had_started.subscribe(self.switch)
        self.switch(master.current_player)
        return self

    _players_moves_animator: proto.MovesAnimator
    _bots_moves_animator: proto.MovesAnimator

    _animator: proto.MovesAnimator

    def get(self) -> proto.MovesAnimator:
        return self._animator

    def switch(self, player: Player) -> None:
        if isinstance(player.inputer, BotPlayerInputer):
            self._animator = self._bots_moves_animator
            return

        self._animator = self._players_moves_animator
