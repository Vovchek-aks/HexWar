from attrs import define

import appearance.protocols as proto


@define
class SwitcherSoundPlayer(proto.SoundPlayer):
    _sound_players: list[proto.SoundPlayer]

    @property
    def is_completed(self) -> bool:
        return self._sound_players[-1].is_completed

    def play(self, speed: float = 1) -> None:
        self.stop()
        sound_player = self._sound_players.pop(0)
        sound_player.play(speed)
        self._sound_players.append(sound_player)

    def stop(self) -> None:
        self._sound_players[-1].stop()

    def copy(self) -> "SwitcherSoundPlayer":
        return SwitcherSoundPlayer([sound_player.copy() for sound_player in self._sound_players])
