from typing import Callable

from appearance.scenes.load_game import load_game
from appearance.scenes.load_main_menu import load_main_menu
from appearance.game_engine.game_engine_arc.window import Window
from appearance.scenes.load_map_editor import load_map_editor
from appearance.scenes.loading_scene import LoadingScene
from core.game_session import GameSession
from mathematics.vector import Vector2Int


def make_main_menu_loading_scene(screen_shape: Vector2Int,
                                 ups: int,
                                 window: Window) -> LoadingScene:
    return LoadingScene.make(screen_shape,
                             load_main_menu(screen_shape, ups, window,
                                            lambda make_game_session: make_game_loading_scene(screen_shape,
                                                                                              ups,
                                                                                              window,
                                                                                              make_game_session)))


def make_game_loading_scene(screen_shape: Vector2Int,
                            ups: int,
                            window: Window,
                            make_game_session: Callable[[], GameSession]) -> LoadingScene:
    return LoadingScene.make(screen_shape,
                             load_game(screen_shape, window, make_game_session,
                                       lambda: make_main_menu_loading_scene(screen_shape, ups, window)))


def make_multibot_loading_scene(screen_shape: Vector2Int,
                                window: Window,
                                make_game_session: Callable[[], GameSession]) -> LoadingScene:
    return LoadingScene.make(screen_shape,
                             load_game(screen_shape, window, make_game_session,
                                       lambda: make_multibot_loading_scene(screen_shape, window, make_game_session),
                                       is_multibot=True))


def make_map_editor_loading_scene(screen_shape: Vector2Int, window: Window) -> LoadingScene:
    return LoadingScene.make(screen_shape, load_map_editor(screen_shape, window))
