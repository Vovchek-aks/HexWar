from typing import Iterator, Callable

from attrs import define, field

import appearance.protocols as proto
from statuses import MISSING, ABORT_NEEDED, Status


@define
class SceneSwitcher(proto.SceneSwitcher):
    @classmethod
    def make(cls, scene: proto.Scene) -> "SceneSwitcher":
        self = cls(scene)
        self._updater = self._scene_switcher()
        return self

    _scene: proto.Scene
    _updater: Iterator[None] | Status = field(init=False, default=MISSING)

    @property
    def scene(self) -> proto.Scene:
        return self._scene

    def update(self, on_game_exit: Callable[[], None]) -> None:
        assert self._updater is not MISSING

        if next(self._updater, ABORT_NEEDED) is ABORT_NEEDED:
            self._updater = MISSING
            on_game_exit()


    def _scene_switcher(self) -> Iterator[None]:
        while True:
            with self.scene:
                if (next_scene := self.scene.next()) is ABORT_NEEDED:
                    return

                if next_scene is not MISSING:
                    self._scene = next_scene

                yield
