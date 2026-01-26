from typing import Callable, Iterator

from appearance.UI.drawer import UiDrawer
from appearance.UI.game_ui_layer_maker import GameUiLayerMaker
from appearance.game_engine.game_engine_arc.frame_drawer import FrameDrawer
from appearance.game_engine.game_engine_arc.input_state import InputState
from appearance.game_engine.game_engine_arc.updater import Updater
from appearance.graphics.camera.camera import CachedCamera, Camera
from appearance.graphics.camera.camera_orientation import CameraOrientation, ReadonlyCameraOrientation
from appearance.graphics.draw import DrawMaker
from appearance.graphics.draw.drawers.drawers_arc.camera_assistant_arc import CameraAssistant
from appearance.graphics.layer_drawers.board_drawable_layer import BoardDrawableLayer
from appearance.graphics.layer_drawers.whole_screen_drawable_layer import WholeScreenDrawableLayer
from appearance.input.camera_mover import CameraMover
from appearance.input.cell_selector import CellSelector
from appearance.input.clicks_catcher.layers.board_layer import BoardLayer
from appearance.input.clicks_catcher.layers.whole_screen_layer import WholeScreenLayer
from appearance.input.mouse_movement_observer import MouseMovementObserver
from appearance.input.moves_inputer import MovesInputer
from appearance.input.moves_inputer.actions_reader import InputActionsReader
from appearance.input.moves_inputer.input_actions import ButtonPressAction
from appearance.input.pause_menu_opener import PauseMenuOpener
from appearance.input.screenshot_saver import ScreenshotSaver
from appearance.input.under_cursor_cell_getter import UnderCursorCellGetter
from appearance.language import Language
from appearance.layer import Layer
from appearance.scenes.game_scene import GameScene
from core.cells_changes_observer import CellsChangesObserver
from core.moves_maker import MovesMaker
from core.player.inputers.event_player_inputer import EventPlayerInputerBuilder
from core.player.player_moves_maker import player_moves_maker
from core.protocols import GameSession
from mathematics.vector import Vector2Int
from observer import Event
from appearance.game_engine.game_engine_arc.window import Window
import appearance.protocols as proto
from statuses import Status


def load_game(screen_shape: Vector2Int,
              window: Window,
              make_session: Callable[[], GameSession],
              make_main_menu_loading_scene: Callable[[], proto.Scene]) -> Iterator[proto.Scene | Status]:
    language = Language.from_meta()

    yield language.get_map_loading_message()
    session = make_session()

    yield language.get_intermediate_preparing_message()
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

    cell_changed_figure = Event[Vector2Int, None]()
    session.figures.figure_was_added_at.subscribe(lambda _, coord: cell_changed_figure.invoke(coord))
    session.figures.figure_was_removed.subscribe(lambda _, coord: cell_changed_figure.invoke(coord))
    session.figures.figure_was_converted.subscribe(lambda _, __, coord: cell_changed_figure.invoke(coord))
    session.figures.figure_was_moved.subscribe(lambda _, coord, __: cell_changed_figure.invoke(coord))
    session.figures.figure_was_moved.subscribe(lambda _, __, coord: cell_changed_figure.invoke(coord))
    cells_change_observer = CellsChangesObserver.make([moves_maker.cell_changed_owner],
                                                      [cell_changed_figure.subscriber])

    cells_change_observer.cell_changed_figure.subscribe(lambda coord: session.cells.update(session.board[coord]))
    cells_change_observer.cell_changed_owner.subscribe(lambda coord: session.cells.update(session.board[coord]))

    cell_selector = CellSelector.make(actions_reader, moves_maker, session.master)
    moves_inputer = MovesInputer.make(actions_reader, session, cell_selector)

    mouse_movement_observer = MouseMovementObserver()

    user_inputer_builder = EventPlayerInputerBuilder()
    user_inputer_builder.set_move_was_read(moves_inputer.move_was_raed)

    pause_menu_open_requested = Event[None]()
    pause_menu_opener = PauseMenuOpener(pause_menu_open_requested.invoke)

    yield language.get_ui_making_message()
    ui_layer = (GameUiLayerMaker(UiDrawer(),
                                 screen_shape,
                                 session,
                                 cell_selector,
                                 mouse_movement_observer,
                                 button_press_action_happened,
                                 moves_maker,
                                 actions_reader)
                .make(user_inputer_builder))

    yield language.get_sprite_loading_message()
    draw = DrawMaker().make(screen_shape, camera, session.board, cells_change_observer)

    camera_assistant = CameraAssistant.make(camera)
    layers = [
        ui_layer,
        Layer(BoardDrawableLayer(draw, hovered_cell_getter, cell_selector, camera_assistant), board_layer),
        Layer(WholeScreenDrawableLayer(draw), null_layer)
    ]
    updater = Updater.make(camera_mover, camera_orientation, screenshot_saver, pause_menu_opener,
                           mouse_movement_observer, layers, player_moves_maker(session, moves_maker))
    drawer = FrameDrawer.make(layers)
    session.master.current_player.change_inputer(user_inputer_builder.build())

    scene = GameScene(drawer, updater, InputState.make(window), make_main_menu_loading_scene)
    pause_menu_open_requested.subscribe(scene.on_pause_menu_open_requested)
    yield scene
