from typing import Callable

from appearance.game_engine.game_engine_arc.game_engine import GameEngine
from appearance.game_engine.game_engine_arc.window import Window
from appearance.protocols import Scene
from appearance.scenes.scene_switcher import SceneSwitcher
from mathematics.vector import Vector2Int


def make_game_engine(caption: str,
                     ups: int,
                     screen_shape: Vector2Int,
                     make_scene: Callable[[Window], Scene]) -> GameEngine:
    window = Window(ups, caption, screen_shape)
    scene_switcher = SceneSwitcher.make(make_scene(window))
    return GameEngine.make(caption, window, scene_switcher)
