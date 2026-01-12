from appearance.game_engine.game_engine_arc.load_game import load_game
from appearance.game_engine.game_engine_arc.load_main_menu import load_main_menu
from appearance.game_engine.game_engine_arc.window import Window
from appearance.scenes.loading_scene import LoadingScene
from core.game_session import multibot_map
from mathematics.vector import Vector2Int


def make_main_menu_loading_scene(screen_shape: Vector2Int, window: Window) -> LoadingScene:
    return LoadingScene.make(screen_shape,
                             load_main_menu(screen_shape,
                                            window,
                                            make_game_loading_scene(screen_shape, window)))


def make_game_loading_scene(screen_shape: Vector2Int, window: Window) -> LoadingScene:
    return LoadingScene.make(screen_shape,
                             load_game(screen_shape,
                                       window,
                                       lambda: multibot_map(board_size=30,
                                                            initial_town_ratio=0.1),
                                       lambda: make_main_menu_loading_scene(screen_shape, window)))
