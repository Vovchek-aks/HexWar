from pathlib import Path
from time import time

from attrs import define, field

import arcade as arc
from pyglet.media import Player as ArcSoundPlayer

from statuses import Status, MISSING
import appearance.protocols as proto


@define
class Sound(proto.SoundPlayer):
    @classmethod
    def load(cls, path: Path, *, volume: float = 1, is_looped: bool = False, is_streaming: bool = False) -> "Sound":
        sound = arc.Sound(path, is_streaming)
        return cls(hash(path), sound, volume, is_looped)

    _hash: int
    _sound: arc.Sound = field(eq=False, hash=False)
    _volume: float = field(eq=False, hash=False)
    _is_looped: bool = field(eq=False, hash=False)
    _player: ArcSoundPlayer | Status = field(init=False, default=MISSING, eq=False, hash=False)
    _time: float = field(init=False, default=0)

    @property
    def duration(self) -> float:
        return self._sound.source.duration

    @property
    def progress(self) -> float:
        return (time() - self._time) / self.duration

    @property
    def is_completed(self) -> bool:  # SHIT
        return self._was_stopped or self.progress >= 1

    @property
    def _was_stopped(self) -> bool:
        return self._player is MISSING

    def play(self, speed: float = 1) -> None:
        self.stop()
        self._time = time()
        self._player = self._sound.play(self._volume, 0, self._is_looped, speed)

    def stop(self) -> None:
        if self._was_stopped:
            return

        self._sound.stop(self._player)
        self._player = MISSING

    def copy(self) -> "Sound":
        return Sound(self._hash, self._sound, self._volume, self._is_looped)
