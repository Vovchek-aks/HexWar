import random
import sys
import psutil
import os

import pyglet

pyglet.options['audio'] = 'openal', 'pulse', 'xaudio2', 'directsound'

from appearance.game_engine import GameEngine
from appearance.game_engine.game_engine_arc.window import Window
from appearance.input.players_selector import PlayersSelector
from appearance.protocols import Scene
from appearance.scenes.loading_scenes_maker import LoadingScenesMaker
from core.game_rules import FiguresUpdateFlagCaller
from core.game_session import GameSession
from core.map_randomizer import MapRandomizer
from core.player.inputers.bot_player_inputer import BotPlayerInputer
from core.player.inputers.bots import BotIgor
from core.resources import Dollars, ResourcesGroup, LightIndustryProducts, HeavyIndustryProducts
from files import read_random_bot_names
from game_session_saver import GameSessionLoader

IS_MULTIBOT = False

UPS = 60
CAPTION = "HexWar"


def main() -> None:
    psutil.Process(os.getpid()).nice(psutil.HIGH_PRIORITY_CLASS)
    sys.setrecursionlimit(10_000)

    make_first_scene = _make_multibot_loading_scene if IS_MULTIBOT else _make_main_menu_loading_scene
    # from game_session_saver import GameSessionSaver
    # from core.game_session import empty_map
    # from game_session_saver import EDIT_MAP_FILE
    # GameSessionSaver(empty_map(board_size=10, player_names=["Russia", "Sweden"])).save(EDIT_MAP_FILE)
    # make_first_scene = _make_map_editor_loading_scene
    make_first_scene = _make_test_game_loading_scene
    with GameEngine.make(CAPTION, UPS, make_first_scene) as engine:
        engine.run()


def _make_test_game_loading_scene(window: Window) -> Scene:
    def make_game_session() -> GameSession:
        session = GameSessionLoader.make("Finnish Gulf.json", UPS).load()
        # player = session.master.players[10]
        player = session.master.current_player
        players_selector = PlayersSelector(session)
        players_selector.toggle(player)
        player.resources.add(ResourcesGroup.make(Dollars(1_000_000_000),
                                                 LightIndustryProducts(1_000_000),
                                                 HeavyIndustryProducts(1_000_000)))
        FiguresUpdateFlagCaller().on_turn_start(session)
        return GameSession(players_selector.make_master(),
                           session.board,
                           session.figures_budget,
                           session.pulling_connections,
                           session.cells,
                           session.figures)

    return LoadingScenesMaker(window, UPS).make_game_loading_scene(make_game_session)


def _make_map_editor_loading_scene(window: Window) -> Scene:
    return LoadingScenesMaker(window, UPS).make_map_editor_loading_scene()


def _make_main_menu_loading_scene(window: Window) -> Scene:
    return LoadingScenesMaker(window, UPS).make_main_menu_loading_scene()


def _make_multibot_loading_scene(window: Window) -> Scene:
    return LoadingScenesMaker(window, UPS).make_multibot_loading_scene(
        lambda: MapRandomizer.make(GameSessionLoader.make(random.choice([
            # "Round Cross.json",
            "SVO.json",
            "Middle East.json",
            "Finnish Gulf.json",
            "Balkans.json"
        ]), UPS).load(), lambda: BotPlayerInputer(BotIgor(), UPS))
        .get_randomized(len(read_random_bot_names()) // 2, ResourcesGroup.make(Dollars(3_000_000)), 10, UPS))

    # return LoadingScenesMaker(window, UPS).make_multibot_loading_scene(
    #     lambda: MapRandomizer.make(GameSessionLoader.make("Balkans.json", UPS).load(),
    #                                lambda: BotPlayerInputer(BotIgor(), UPS))
    #     .get_randomized(len(read_random_bot_names()), ResourcesGroup.make(Dollars(3_000_000)), 10, UPS))
    #
    # return LoadingScenesMaker(window, UPS).make_multibot_loading_scene(
    #     lambda: MapRandomizer.make(GameSessionLoader.make("Balkans.json", UPS).load(),
    #                                lambda: BotPlayerInputer(BotIgor(), UPS))
    #     .get_randomized(len(read_random_bot_names()) // 2, ResourcesGroup.make(Dollars(3_000_000)), 10, UPS))

    # return LoadingScenesMaker(window, UPS).make_multibot_loading_scene(
    #     lambda: GameSessionLoader.make("_edit_map.json", UPS).load()
    # )


if __name__ == '__main__':
    main()
