from appearance.UI.drawer import UiDrawer
from appearance.UI.ui_layer_maker import UiLayerMaker
from appearance.game_engine.game_engine_arc.game_engine import GameEngine
from appearance.game_engine.game_engine_arc.updater import Updater
from appearance.game_engine.game_engine_arc.window import Window
from appearance.graphics.layer_drawers.board_drawable_layer import BoardDrawableLayer
from appearance.graphics.layer_drawers.whole_screen_drawable_layer import WholeScreenDrawableLayer
from appearance.graphics.sprites import SpritesLoader
from appearance.input.mouse_movement_observer import MouseMovementObserver
from appearance.input.moves_inputer.input_actions import ButtonPressAction
from appearance.input.screenshot_saver import ScreenshotSaver
from appearance.layer import Layer
from core.player.player_moves_maker import player_moves_maker
from mathematics.vector import Vector2Int, Vector2
from appearance.graphics.camera.camera import Camera, CachedCamera
from appearance.graphics.camera.camera_orientation import CameraOrientation, ReadonlyCameraOrientation
from appearance.graphics.draw import DrawMaker
from appearance.input.cell_selector import CellSelector
from appearance.input.clicks_catcher.layers.board_layer import BoardLayer
from appearance.input.clicks_catcher.layers.whole_screen_layer import WholeScreenLayer
from appearance.input.moves_inputer import MovesInputer
from appearance.input.moves_inputer.actions_reader import InputActionsReader
from appearance.input.under_cursor_cell_getter import UnderCursorCellGetter
from core.moves_maker import MovesMaker
from appearance.game_engine.game_engine_arc.input_state import InputState
from appearance.game_engine.game_engine_arc.frame_drawer import FrameDrawer
from appearance.input.camera_mover import CameraMover
from core.player.inputers.event_player_inputer import EventPlayerInputerBuilder, EventPlayerInputer
from core.protocols import GameSession
from observer import Event


def make_game_engine(caption: str,
                     ups: int,
                     screen_shape: Vector2Int,
                     session: GameSession) -> tuple[GameEngine, EventPlayerInputer]:
    window = Window(ups, caption, screen_shape)

    # _blit_loading_screen(screen_shape)

    screenshot_saver = ScreenshotSaver()

    camera_orientation = CameraOrientation.starter()
    camera_mover = CameraMover(camera_orientation)
    camera = CachedCamera.make(Camera(screen_shape.as_vector2, ReadonlyCameraOrientation(camera_orientation)))

    hovered_cell_getter = UnderCursorCellGetter(camera, session.board)

    board_layer = BoardLayer(hovered_cell_getter)
    null_layer = WholeScreenLayer()

    button_press_action_happened = Event[ButtonPressAction, None]()
    actions_reader = InputActionsReader.make(board_layer, null_layer, button_press_action_happened.subscriber)

    moves_maker = MovesMaker(session)
    cell_selector = CellSelector.make(actions_reader, moves_maker, session.master)
    moves_inputer = MovesInputer.make(actions_reader, session, cell_selector)

    mouse_movement_observer = MouseMovementObserver()

    user_inputer_builder = EventPlayerInputerBuilder()
    user_inputer_builder.set_move_was_read(moves_inputer.move_was_raed)
    ui_layer = (UiLayerMaker(UiDrawer(),
                             screen_shape,
                             session,
                             cell_selector,
                             mouse_movement_observer,
                             button_press_action_happened,
                             moves_maker,
                             actions_reader)
                .make(user_inputer_builder))

    draw = DrawMaker().make(screen_shape, camera, session.board, moves_maker)

    layers = [
        ui_layer,
        Layer(BoardDrawableLayer(draw, hovered_cell_getter, cell_selector), board_layer),
        Layer(WholeScreenDrawableLayer(draw), null_layer)
    ]

    updater = Updater.make(camera_mover, camera_orientation, screenshot_saver, mouse_movement_observer, layers,
                           player_moves_maker(session, moves_maker))
    drawer = FrameDrawer.make(layers)

    input_state = InputState.make(window)

    return (GameEngine.make(caption, window, drawer, updater, input_state),
            user_inputer_builder.build())


def _blit_loading_screen(screen_shape: Vector2Int) -> None:
    loading = SpritesLoader.from_meta().load_loading_screen()
    loading = loading.reshape(screen_shape)
    loading.blit_at(Vector2.zero())
