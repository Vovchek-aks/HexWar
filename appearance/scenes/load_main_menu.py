from typing import Iterator, Callable

from attrs import frozen

from appearance.UI.drawer import UiDrawer
from appearance.UI.image import ImageUi
from appearance.UI.main_menu_ui_layer_maker import MainMenuUiLayerMaker
from appearance.game_engine.game_engine_arc.input_state import InputState
from appearance.graphics.layer_drawers.whole_screen_drawable_layer import WholeScreenDrawableLayer
from appearance.graphics.sprites import SpritesLoader
from appearance.input.clicks_catcher.layers.whole_screen_layer import WholeScreenLayer
from appearance.input.screenshot_saver import ScreenshotSaver
from appearance.language import Language
from appearance.layer import Layer
from appearance.scenes.loading_scene import LoadingScene
from appearance.scenes.main_menu_scene import MainMenuScene
from appearance.settings import Settings
from core.map_randomizer import MapRandomizer
from core.player.inputers.bot_player_inputer import BotPlayerInputer
from core.player.inputers.bots import BotIgor
from core.protocols import GameSession
from core.resources import ResourcesGroup, Dollars
from game_session_saver import GameSessionLoader, SAVE_FILE, is_tutorial
from mathematics.rectangle import Rectangle
from mathematics.vector import Vector2
from observer import Event
from appearance.game_engine.game_engine_arc.window import Window
import appearance.protocols as proto
from statuses import Status, MISSING

FromSessionMakerLoadingSceneGetter = Callable[[Callable[[], GameSession]], LoadingScene]


def load_main_menu(ups: int,
                   window: Window,
                   get_player_selection_loading_scene: FromSessionMakerLoadingSceneGetter,
                   get_game_loading_scene: FromSessionMakerLoadingSceneGetter,
                   get_tutorial_game_loading_scene_getter: Callable[[str], FromSessionMakerLoadingSceneGetter],
                   ) -> Iterator[proto.Scene | Status]:
    screen_shape = Settings.open().screen_shape
    language = Language.from_meta()

    yield language.get_intermediate_preparing_message()
    screenshot_saver = ScreenshotSaver()

    null_layer = WholeScreenLayer()

    map_was_selected = Event[str, Status | int, None]()
    exit_was_pressed = Event[None]()
    reload_was_pressed = Event[None]()

    yield language.get_ui_making_message()
    drawer = UiDrawer()
    ui_layer = (MainMenuUiLayerMaker(drawer, screen_shape)
                .make(map_was_selected.invoke, exit_was_pressed.invoke, reload_was_pressed.invoke))

    yield language.get_sprite_loading_message()
    background = SpritesLoader.from_meta().load_menu_background()
    rectangle = Rectangle(Vector2.zero(), screen_shape.as_vector2)

    layers = [
        ui_layer,
        Layer(WholeScreenDrawableLayer(Draw(ImageUi.make(drawer, rectangle, background))), null_layer)
    ]

    scene = MainMenuScene.make(screenshot_saver, InputState.make(window), layers)

    def on_map_was_selected(map_name: str, random_players_count: Status | int) -> None:
        scene_loader = scene_loader_from(map_name)
        if random_players_count is MISSING:
            scene.switch_to(scene_loader(lambda: GameSessionLoader
                                         .make(f"{map_name}.json", ups)
                                         .load()))
            return
        scene.switch_to(scene_loader(lambda: MapRandomizer.make(GameSessionLoader
                                                                .make(f"{map_name}.json", ups)
                                                                .load(),
                                                                lambda: BotPlayerInputer(BotIgor(), ups))
                                     .with_players_count(random_players_count, ResourcesGroup.make(Dollars(3_000_000)),
                                                         10, ups)))

    def scene_loader_from(map_name: str) -> FromSessionMakerLoadingSceneGetter:
        if is_tutorial(map_name):
            return get_tutorial_game_loading_scene_getter(map_name)

        if map_name == SAVE_FILE.stem:
            return get_game_loading_scene

        return get_player_selection_loading_scene

    def reload() -> None:
        settings = Settings.open()
        screen_shape = settings.screen_shape
        window.change_is_fullscreen(True)
        window.change_is_fullscreen(False)
        window.change_screen_shape(screen_shape)
        window.change_is_fullscreen(settings.if_fullscreen)
        scene.switch_to(LoadingScene.make(load_main_menu(ups,
                                                         window,
                                                         get_player_selection_loading_scene,
                                                         get_game_loading_scene,
                                                         get_tutorial_game_loading_scene_getter)))

    map_was_selected.subscribe(on_map_was_selected)
    exit_was_pressed.subscribe(scene.on_exit_was_pressed)
    reload_was_pressed.subscribe(reload)

    yield scene


@frozen
class Draw:
    _background: ImageUi

    def background(self) -> None:
        self._background.layer.draw(Vector2.zero())
