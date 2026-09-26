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

UPS = 60
CAPTION = "HexWar"


def main() -> None:
    # from game_session_saver import _get_all_maps, GameSessionSaver
    # for file in _get_all_maps():
    #     GameSessionSaver(GameSessionLoader.make(f"{file}.json", 60).load()).save(f"{file}.json")
    # return

    psutil.Process(os.getpid()).nice(psutil.HIGH_PRIORITY_CLASS)
    sys.setrecursionlimit(10_000)
    make_first_scene = _make_test_game_loading_scene
    # make_first_scene = _make_multibot_loading_scene
    # make_first_scene = _make_map_editor_loading_scene
    # make_first_scene = _make_main_menu_loading_scene
    with GameEngine.make(CAPTION, UPS, make_first_scene) as engine:
        engine.run()


def _make_test_game_loading_scene(window: Window) -> Scene:
    def make_game_session() -> GameSession:
        session = GameSessionLoader.make("_map_from_editor.json", UPS).load()
        # player = session.master.current_player
        player = session.master.players[1]
        players_selector = PlayersSelector(session)
        players_selector.toggle(player)
        player.resources.add(ResourcesGroup.make(Dollars(1_000_000_000),
                                                 LightIndustryProducts(1_000_000),
                                                 HeavyIndustryProducts(1_000_000)))
        return session.with_master(players_selector.make_master())

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
    #     lambda: GameSessionLoader.make("_map_from_editor.json", UPS).load()
    # )


if __name__ == '__main__':
    main()
