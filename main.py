from appearance.game_engine import make_game_engine
from appearance.scenes.loading_scenes_makers import make_main_menu_loading_scene
from mathematics.vector import Vector2Int

SCREEN_SHAPE = Vector2Int(1280, 720)
UPS = 60
CAPTION = "HexWar"


def main() -> None:
    engine = make_game_engine(CAPTION, UPS, SCREEN_SHAPE, make_main_menu_loading_scene)

    with engine:
        engine.run()


if __name__ == '__main__':
    main()
