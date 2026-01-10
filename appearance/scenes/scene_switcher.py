from typing import Iterator

from attrs import define, field

import appearance.protocols as proto
from statuses import MISSING


@define
class SceneSwitcher(proto.SceneSwitcher):
    @classmethod
    def make(cls, scene: proto.Scene) -> "SceneSwitcher":
        self = cls(scene)
        self._updater = self._scene_switcher()
        return self

    _scene: proto.Scene
    _updater: Iterator[None] = field(init=False)

    @property
    def scene(self) -> proto.Scene:
        return self._scene

    def update(self) -> None:
        next(self._updater)

    def _scene_switcher(self) -> Iterator[None]:
        while True:
            with self.scene:
                if (next_scene := self.scene.next()) is not MISSING:
                    self._scene = next_scene
                yield
