import random

from attrs import define, field

from appearance.audio.sound.sound_player import Sound
from appearance.audio.sound.sounds_loader import SoundsLoader
from statuses import Status, MISSING

_TO_SWITCH_PROGRESS = .8


@define
class MusicPlayer:
    @classmethod
    def load(cls) -> "MusicPlayer":
        return cls(SoundsLoader.load_music())

    @classmethod
    def empty(cls) -> "MusicPlayer":
        return cls([SoundsLoader.from_meta().load_empty()] * 2)

    _playlist: list[Sound]
    _current: Sound = field(factory=lambda: SoundsLoader.from_meta().load_empty())
    _previous: Sound | Status = field(init=False, default=MISSING)

    def update(self) -> None:
        if self._previous is not MISSING and self._previous.is_completed:
            self._previous.stop()
            self._previous = MISSING

        if self._current.progress > _TO_SWITCH_PROGRESS:
            self._switch()

    def stop(self) -> None:
        if self._previous is not MISSING:
            self._previous.stop()
        self._current.stop()

    def _switch(self) -> None:
        if self._previous is not MISSING:
            self._previous.stop()

        self._previous = self._current

        candidates = list(self._playlist)
        if self._current in candidates:
            candidates.remove(self._current)
        self._current = random.choice(candidates)
        self._current.play()
