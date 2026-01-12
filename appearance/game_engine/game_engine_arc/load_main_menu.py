from typing import Iterator

from attrs import frozen

from appearance.UI.drawer import UiDrawer
from appearance.UI.main_menu_ui_layer_maker import MainMenuUiLayerMaker
from appearance.game_engine.game_engine_arc.input_state import InputState
from appearance.graphics.draw.drawers.drawers_arc.background_drawer import BackgroundDrawer
from appearance.graphics.layer_drawers.whole_screen_drawable_layer import WholeScreenDrawableLayer
from appearance.input.clicks_catcher.layers.whole_screen_layer import WholeScreenLayer
from appearance.input.screenshot_saver import ScreenshotSaver
from appearance.language import Language
from appearance.layer import Layer
from appearance.scenes.loading_scene import LoadingScene
from appearance.scenes.main_menu_scene import MainMenuScene
from mathematics.vector import Vector2Int
from observer import Event
from appearance.game_engine.game_engine_arc.window import Window
import appearance.protocols as proto
from statuses import Status


def load_main_menu(screen_shape: Vector2Int,
                   window: Window,
                   game_loading_scene: LoadingScene) -> Iterator[proto.Scene | Status]:
    language = Language.from_meta()

    yield language.get_intermediate_preparing_message()
    screenshot_saver = ScreenshotSaver()

    null_layer = WholeScreenLayer()

    play_was_pressed = Event[None]()
    exit_was_pressed = Event[None]()

    yield language.get_ui_making_message()
    ui_layer = (MainMenuUiLayerMaker(UiDrawer(),
                                     screen_shape)
                .make(play_was_pressed.invoke,
                      exit_was_pressed.invoke))

    yield language.get_sprite_loading_message()

    @frozen  # shit code
    class Draw:
        _background_drawer: BackgroundDrawer

        def background(self) -> None:
            self._background_drawer.draw_background()

    layers = [
        ui_layer,
        Layer(WholeScreenDrawableLayer(Draw(BackgroundDrawer(screen_shape))), null_layer)
    ]

    scene = MainMenuScene.make(screenshot_saver, InputState.make(window), layers)
    play_was_pressed.subscribe(lambda: scene.on_play_was_pressed(game_loading_scene))
    exit_was_pressed.subscribe(scene.on_exit_was_pressed)
    yield scene
