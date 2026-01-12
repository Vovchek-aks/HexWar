from typing import Callable

from appearance.game_engine.game_engine_arc.load_game import load_game
from appearance.game_engine.game_engine_arc.load_main_menu import load_main_menu
from appearance.game_engine.game_engine_arc.window import Window
from appearance.scenes.loading_scene import LoadingScene
from core.game_session import multibot_map, GameSession
from mathematics.vector import Vector2Int


def make_main_menu_loading_scene(screen_shape: Vector2Int,
                                 window: Window,
                                 make_game_session: Callable[[], GameSession]) -> LoadingScene:
    return LoadingScene.make(screen_shape,
                             load_main_menu(screen_shape,
                                            window,
                                            make_game_loading_scene(screen_shape, window, make_game_session)))


def make_game_loading_scene(screen_shape: Vector2Int,
                            window: Window,
                            make_game_session: Callable[[], GameSession]) -> LoadingScene:
    return LoadingScene.make(screen_shape,
                             load_game(screen_shape,
                                       window,
                                       make_game_session,
                                       lambda: make_main_menu_loading_scene(screen_shape, window)))
