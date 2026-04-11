import sys

from appearance.game_engine import GameEngine
from appearance.game_engine.game_engine_arc.window import Window
from appearance.input.players_selector import PlayersSelector
from appearance.protocols import Scene
from appearance.scenes.loading_scenes_maker import LoadingScenesMaker
from core.game_session import GameSession
from core.resources import Dollars, ResourcesGroup, LightIndustryProducts, HeavyIndustryProducts
from game_session_saver import GameSessionLoader
from mathematics.vector import Vector2Int

IS_MULTIBOT = False

IS_FULLSCREEN = False
SCREEN_SHAPE = (Vector2Int(1920, 1080)
                if IS_FULLSCREEN else
                Vector2Int(1280, 720))

UPS = 60
CAPTION = "HexWar"


def main() -> None:
    sys.setrecursionlimit(10_000)

    make_first_scene = _make_multibot_loading_scene if IS_MULTIBOT else _make_main_menu_loading_scene
    # from game_session_saver import GameSessionSaver
    # from core.game_session import empty_map
    # from game_session_saver import EDIT_MAP_FILE
    # GameSessionSaver(empty_map(board_size=75, player_names=["Red", "Albania"])).save(EDIT_MAP_FILE)
    # make_first_scene = _make_map_editor_loading_scene
    make_first_scene = _make_test_game_loading_scene
    with GameEngine.make(CAPTION, UPS, IS_FULLSCREEN, SCREEN_SHAPE, make_first_scene) as engine:
        engine.run()


def _make_test_game_loading_scene(screen_shape: Vector2Int, window: Window) -> Scene:
    def make_game_session() -> GameSession:
        session = GameSessionLoader.make("Balkans.json", UPS).load()
        players_selector = PlayersSelector(session)
        players_selector.toggle(session.master.current_player)
        session.master.current_player.resources.add(ResourcesGroup.make(Dollars(100_000_000),
                                                                        LightIndustryProducts(1_000_000),
                                                                        HeavyIndustryProducts(1_000_000)))
        return GameSession(players_selector.make_master(),
                           session.board,
                           session.figures_budget,
                           session.pulling_connections,
                           session.cells,
                           session.figures)

    return LoadingScenesMaker(screen_shape, window, UPS).make_game_loading_scene(make_game_session)


def _make_map_editor_loading_scene(screen_shape: Vector2Int, window: Window) -> Scene:
    return LoadingScenesMaker(screen_shape, window, UPS).make_map_editor_loading_scene()


def _make_main_menu_loading_scene(screen_shape: Vector2Int, window: Window) -> Scene:
    return LoadingScenesMaker(screen_shape, window, UPS).make_main_menu_loading_scene()


def _make_multibot_loading_scene(screen_shape: Vector2Int, window: Window) -> Scene:
    return LoadingScenesMaker(screen_shape, window, UPS).make_multibot_loading_scene(
        lambda: GameSessionLoader.make("Balkans.json", UPS).load())


if __name__ == '__main__':
    main()
