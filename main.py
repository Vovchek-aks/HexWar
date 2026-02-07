from appearance.game_engine import GameEngine
from appearance.game_engine.game_engine_arc.window import Window
from appearance.protocols import Scene
from appearance.scenes.loading_scenes_makers import make_main_menu_loading_scene, make_multibot_loading_scene
from core.game_session import multibot_map
from mathematics.vector import Vector2Int

IS_MULTIBOT = True

IS_FULLSCREEN = False
SCREEN_SHAPE = (Vector2Int(1920, 1080)
                if IS_FULLSCREEN else
                Vector2Int(1280, 720))

UPS = 60
CAPTION = "HexWar"


def main() -> None:
    make_first_scene = _make_multibot_loading_scene if IS_MULTIBOT else _make_main_menu_loading_scene
    with GameEngine.make(CAPTION, UPS, IS_FULLSCREEN, SCREEN_SHAPE, make_first_scene) as engine:
        engine.run()


def _make_main_menu_loading_scene(screen_shape: Vector2Int, window: Window) -> Scene:
    return make_main_menu_loading_scene(screen_shape, window,
                                        lambda: multibot_map(ups=UPS, board_size=70, initial_town_ratio=.75))


def _make_multibot_loading_scene(screen_shape: Vector2Int, window: Window) -> Scene:
    return make_multibot_loading_scene(screen_shape, window,
                                       lambda: multibot_map(ups=UPS, board_size=70, initial_town_ratio=.75))


if __name__ == '__main__':
    main()
