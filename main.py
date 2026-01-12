from appearance.game_engine import GameEngine
from appearance.scenes.loading_scenes_makers import make_main_menu_loading_scene
from mathematics.vector import Vector2Int

SCREEN_SHAPE = Vector2Int(1280, 720)
UPS = 60
CAPTION = "HexWar"


def main() -> None:
    with GameEngine.make(CAPTION, UPS, SCREEN_SHAPE, make_main_menu_loading_scene) as engine:
        engine.run()


if __name__ == '__main__':
    main()
