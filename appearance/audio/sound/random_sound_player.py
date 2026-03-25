import random

from attrs import define, field

import appearance.protocols as proto


@define
class RandomSoundPlayer(proto.SoundPlayer):
    _sound_players: list[proto.SoundPlayer]
    _is_repetitions_allowed: bool = False
    _is_multiple_sounds_to_play_at_ones_allowed: bool = False

    _currently_playing: list[proto.SoundPlayer] = field(init=False, factory=list)

    @property
    def is_completed(self) -> bool:
        return all(sound_player.is_completed for sound_player in self._currently_playing)

    def play(self, speed: float = 1) -> None:
        sound_player = self._get_next_sound_player()

        if not self._is_multiple_sounds_to_play_at_ones_allowed:
            self.stop()

        self._remove_completed_from_currently_playing()
        sound_player.play()
        self._currently_playing.append(sound_player)

    def stop(self) -> None:
        for sound_player in self._currently_playing:
            sound_player.stop()
        self._currently_playing.clear()

    def copy(self) -> "RandomSoundPlayer":
        return RandomSoundPlayer([sound_player.copy() for sound_player in self._sound_players],
                                 self._is_repetitions_allowed,
                                 self._is_multiple_sounds_to_play_at_ones_allowed)

    def _get_next_sound_player(self) -> proto.SoundPlayer:
        sound_player: proto.SoundPlayer = random.choice(self._sound_players)
        if self._is_repetitions_allowed:
            return sound_player.copy()

        while sound_player in self._currently_playing:
            sound_player = random.choice(self._sound_players)
        return sound_player.copy()

    def _remove_completed_from_currently_playing(self) -> None:
        to_keep = list[proto.SoundPlayer]()
        for sound_player in self._currently_playing:
            if sound_player.is_completed:
                sound_player.stop()
                continue
            to_keep.append(sound_player)

        self._currently_playing = to_keep
