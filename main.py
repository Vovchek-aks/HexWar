from appearance.game_engine import GameEngine
from appearance.game_engine.game_engine_arc.window import Window
from appearance.protocols import Scene
from appearance.scenes.loading_scenes_makers import make_main_menu_loading_scene
from core.game_session import multibot_map
from mathematics.vector import Vector2Int

SCREEN_SHAPE = Vector2Int(1280, 720)
UPS = 60
CAPTION = "HexWar"


def main() -> None:
    with GameEngine.make(CAPTION, UPS, SCREEN_SHAPE, _make_main_menu_loading_scene) as engine:
        engine.run()


def _make_main_menu_loading_scene(screen_shape: Vector2Int, window: Window) -> Scene:
    return make_main_menu_loading_scene(screen_shape, window,
                                        lambda: multibot_map(board_size=50, initial_town_ratio=0.1))


if __name__ == '__main__':
    main()
