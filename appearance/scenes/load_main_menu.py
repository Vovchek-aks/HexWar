from typing import Iterator, Callable

from attrs import frozen

from appearance.UI.drawer import UiDrawer
from appearance.UI.main_menu_ui_layer_maker import MainMenuUiLayerMaker
from appearance.game_engine.game_engine_arc.input_state import InputState
from appearance.graphics.draw.drawers.drawers_arc.background_drawer import BackgroundDrawer
from appearance.graphics.colors import BACKGROUND
from appearance.graphics.layer_drawers.whole_screen_drawable_layer import WholeScreenDrawableLayer
from appearance.input.clicks_catcher.layers.whole_screen_layer import WholeScreenLayer
from appearance.input.screenshot_saver import ScreenshotSaver
from appearance.language import Language
from appearance.layer import Layer
from appearance.scenes.loading_scene import LoadingScene
from appearance.scenes.main_menu_scene import MainMenuScene
from core.protocols import GameSession
from game_session_saver import GameSessionLoader, SAVE_FILE, is_tutorial
from mathematics.vector import Vector2Int
from observer import Event
from appearance.game_engine.game_engine_arc.window import Window
import appearance.protocols as proto
from statuses import Status

FromSessionMakerLoadingSceneGetter = Callable[[Callable[[], GameSession]], LoadingScene]


def load_main_menu(screen_shape: Vector2Int,
                   ups: int,
                   window: Window,
                   get_player_selection_loading_scene: FromSessionMakerLoadingSceneGetter,
                   get_game_loading_scene: FromSessionMakerLoadingSceneGetter
                   ) -> Iterator[proto.Scene | Status]:
    language = Language.from_meta()

    yield language.get_intermediate_preparing_message()
    screenshot_saver = ScreenshotSaver()

    null_layer = WholeScreenLayer()

    map_was_selected = Event[str, None]()
    exit_was_pressed = Event[None]()

    yield language.get_ui_making_message()
    ui_layer = (MainMenuUiLayerMaker(UiDrawer(), screen_shape)
                .make(map_was_selected.invoke, exit_was_pressed.invoke))

    yield language.get_sprite_loading_message()

    layers = [
        ui_layer,
        Layer(WholeScreenDrawableLayer(Draw(BackgroundDrawer(screen_shape, BACKGROUND))), null_layer)
    ]

    scene = MainMenuScene.make(screenshot_saver, InputState.make(window), layers)

    def on_map_was_selected(map_name: str) -> None:
        scene_loader = scene_loader_from(map_name)
        scene.on_map_was_selected(scene_loader(lambda: GameSessionLoader
                                               .make(f"{map_name}.json", ups)
                                               .load()))

    def scene_loader_from(map_name: str) -> FromSessionMakerLoadingSceneGetter:
        if map_name == SAVE_FILE.stem or is_tutorial(map_name):
            return get_game_loading_scene
        return get_player_selection_loading_scene

    map_was_selected.subscribe(on_map_was_selected)
    exit_was_pressed.subscribe(scene.on_exit_was_pressed)

    yield scene


@frozen
class Draw:
    _background_drawer: BackgroundDrawer

    def background(self) -> None:
        self._background_drawer.draw_background()
