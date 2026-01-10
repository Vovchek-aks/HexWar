from appearance.game_engine import make_game_engine
from appearance.game_engine.game_engine_arc.load_game import load_game
from appearance.game_engine.game_engine_arc.window import Window
from appearance.scenes.loading_scene import LoadingScene
from core.game_session import multibot_map
from mathematics.vector import Vector2Int

SCREEN_SHAPE = Vector2Int(1280, 720)
UPS = 60
CAPTION = "HexWar"


def main() -> None:
    engine = make_game_engine(CAPTION, UPS, SCREEN_SHAPE, _make_loading_scene)

    with engine:
        engine.run()


def _make_loading_scene(window: Window) -> LoadingScene:
    return LoadingScene.make(SCREEN_SHAPE,
                             load_game(SCREEN_SHAPE, window,
                                       lambda: multibot_map(board_size=30,
                                                            initial_town_ratio=0.1)))


if __name__ == '__main__':
    main()
