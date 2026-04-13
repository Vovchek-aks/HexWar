import random

from attrs import define, field

from appearance.audio.sound.sound_player import Sound
from appearance.audio.sound.sounds_loader import SoundsLoader
from statuses import Status, MISSING

_SWITCHING_INSET = 5
_TO_REPEAT_PASSES = 5


@define
class MusicPlayer:
    @classmethod
    def load(cls) -> "MusicPlayer":
        return cls(SoundsLoader.from_meta().load_game_music())

    _playlist: list[Sound]
    _current: Sound = field(factory=lambda: SoundsLoader.from_meta().load_empty())
    _previous: Sound | Status = field(init=False, default=MISSING)
    _history: list[Sound] = field(init=False, factory=list)

    def update(self) -> None:
        if self._previous is not MISSING and self._previous.is_completed:
            self._previous.stop()
            self._previous = MISSING

        if self._current.time > self._current.duration - _SWITCHING_INSET:
            self._switch()

    def stop(self) -> None:
        if self._previous is not MISSING:
            self._previous.stop()
        self._current.stop()

    def _switch(self) -> None:
        if self._previous is not MISSING:
            self._previous.stop()

        self._previous = self._current
        self._history.append(self._previous)
        if len(self._history) > _TO_REPEAT_PASSES:
            self._history.pop(0)

        candidates = list(set(self._playlist) - set(self._history))
        self._current = random.choice(candidates)
        print(self._playlist.index(self._current))
        self._current.play()


@define
class NoMusicPlayer(MusicPlayer):
    _playlist: list[Sound] = field(factory=list)

    def update(self) -> None:
        ...
