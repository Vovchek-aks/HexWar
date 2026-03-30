from typing import Callable

from attrs import frozen

from appearance.scenes.load_game import load_game
from appearance.scenes.load_main_menu import load_main_menu
from appearance.game_engine.game_engine_arc.window import Window
from appearance.scenes.load_map_editor import load_map_editor
from appearance.scenes.load_players_selection import load_players_selection
from appearance.scenes.load_tutorial import load_tutorial
from appearance.scenes.loading_scene import LoadingScene
from core.game_session import GameSession
from mathematics.vector import Vector2Int

GameSessionMaker = Callable[[], GameSession]


@frozen
class LoadingScenesMaker:
    _screen_shape: Vector2Int
    _window: Window
    _ups: int

    def make_main_menu_loading_scene(self) -> LoadingScene:
        return LoadingScene.make(self._screen_shape,
                                 load_main_menu(self._screen_shape, self._ups, self._window,
                                                self.make_player_selection_loading_scene,
                                                self.make_game_loading_scene,
                                                self.make_tutorial_loading_scene_getter))

    def make_player_selection_loading_scene(self, make_game_session: GameSessionMaker) -> LoadingScene:
        return LoadingScene.make(self._screen_shape,
                                 load_players_selection(self._screen_shape,
                                                        lambda game_session: self.make_game_loading_scene(
                                                            lambda: game_session),
                                                        self.make_main_menu_loading_scene,
                                                        make_game_session,
                                                        self._window))

    def make_game_loading_scene(self, make_game_session: GameSessionMaker) -> LoadingScene:
        return LoadingScene.make(self._screen_shape,
                                 load_game(self._screen_shape, self._window, make_game_session,
                                           self.make_main_menu_loading_scene))

    def make_tutorial_loading_scene_getter(self, map_name: str) -> Callable[[GameSessionMaker], LoadingScene]:
        def make_tutorial_loading_scene(make_game_session: GameSessionMaker):
            return LoadingScene.make(self._screen_shape,
                                     load_tutorial(self._screen_shape, self._window, make_game_session,
                                                   self.make_main_menu_loading_scene, int(map_name.split()[-1])))

        return make_tutorial_loading_scene

    def make_multibot_loading_scene(self, make_game_session: GameSessionMaker) -> LoadingScene:
        return LoadingScene.make(self._screen_shape,
                                 load_game(self._screen_shape, self._window, make_game_session,
                                           lambda: self.make_multibot_loading_scene(make_game_session),
                                           is_multibot=True))

    def make_map_editor_loading_scene(self) -> LoadingScene:
        return LoadingScene.make(self._screen_shape, load_map_editor(self._screen_shape, self._window))
