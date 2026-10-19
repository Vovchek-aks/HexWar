from appearance.game_engine.game_engine_arc.window import Window
from appearance.scenes.loading_scene import LoadingScene, PROCESS
from appearance.settings import Settings
import appearance.protocols as proto


def reload(window: Window, scene: proto.SceneWithSwitchTo, process: PROCESS, *, need_to_resize: bool = True) -> None:
    if need_to_resize:
        settings = Settings.open()
        screen_shape = settings.screen_shape
        window.change_is_fullscreen(False, screen_shape=screen_shape)
        window.change_screen_shape(screen_shape)
        window.change_is_fullscreen(settings.if_fullscreen, screen_shape=screen_shape)

    scene.switch_to(LoadingScene.make(process))
