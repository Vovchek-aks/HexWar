from typing import Iterator

from appearance.UI.drawer import UiDrawer
from appearance.UI.map_editor_ui_layer_maker import MapEditorUiLayerMaker
from appearance.game_engine.game_engine_arc.input_state import InputState
from appearance.graphics.camera.camera import CachedCamera, Camera
from appearance.graphics.camera.camera_orientation import CameraOrientation, ReadonlyCameraOrientation
from appearance.graphics.draw import DrawMaker
from appearance.graphics.draw.drawers.drawers_arc.camera_assistant_arc import CameraAssistant
from appearance.graphics.draw.drawers.drawers_arc.on_board_sprites_drawer import OnBoardSpritesDrawer
from appearance.graphics.layer_drawers.map_editor_board_drawable_layer import MapEditorBoardDrawableLayer
from appearance.graphics.layer_drawers.whole_screen_drawable_layer import WholeScreenDrawableLayer
from appearance.input.camera_mover import CameraMover
from appearance.input.clicks_catcher.layers.board_layer import BoardLayer
from appearance.input.clicks_catcher.layers.whole_screen_layer import WholeScreenLayer
from appearance.input.moves_inputer.actions_reader import InputActionsReader
from appearance.input.moves_inputer.input_actions import ButtonPressAction
from appearance.input.screenshot_saver import ScreenshotSaver
from appearance.input.under_cursor_cell_getter import UnderCursorCellGetter
from appearance.language import Language
from appearance.layer import Layer
from appearance.scenes.map_editor_scene import MapEditorScene
from core.cells_changes_observer import CellsChangesObserver
from core.player.players_moves_maker import on_turn_start
from game_session_saver import GameSessionSaver, GameSessionLoader, EDIT_MAP_FILE
from map_editor import MapEditor
from mathematics.vector import Vector2Int
from observer import Event
from appearance.game_engine.game_engine_arc.window import Window
import appearance.protocols as proto
from statuses import Status


def load_map_editor(screen_shape: Vector2Int,
                    window: Window) -> Iterator[proto.Scene | Status]:
    language = Language.from_meta()

    yield language.get_map_loading_message()
    session = GameSessionLoader.make(EDIT_MAP_FILE, 60).load()

    yield language.get_intermediate_preparing_message()
    screenshot_saver = ScreenshotSaver()

    camera_orientation = CameraOrientation.starter()
    camera_mover = CameraMover(camera_orientation)
    camera = CachedCamera.make(Camera(screen_shape.as_vector2, ReadonlyCameraOrientation(camera_orientation)))

    hovered_cell_getter = UnderCursorCellGetter(camera, session.board)

    board_layer = BoardLayer(hovered_cell_getter)
    null_layer = WholeScreenLayer()

    button_press_action_happened = Event[ButtonPressAction, None]()
    actions_reader = InputActionsReader.make(board_layer,
                                             null_layer,
                                             button_press_action_happened.subscriber)

    cell_changed_owner = Event[Vector2Int, None]()
    map_editor = MapEditor.make(session, actions_reader, cell_changed_owner.invoke)

    cell_changed_figure = Event[Vector2Int, None]()
    session.figures.figure_was_added_at.subscribe(lambda _, coord: cell_changed_figure.invoke(coord))
    session.figures.figure_was_removed.subscribe(lambda _, coord: cell_changed_figure.invoke(coord))
    cells_change_observer = CellsChangesObserver.make([cell_changed_owner.subscriber],
                                                      [cell_changed_figure.subscriber])
    cells_change_observer.cell_changed_figure.subscribe(lambda coord: session.cells.update(session.board[coord]))
    cells_change_observer.cell_changed_owner.subscribe(lambda coord: session.cells.update(session.board[coord]))

    yield language.get_ui_making_message()
    exit_was_pressed = Event[None]()
    ui_layer_maker = MapEditorUiLayerMaker(UiDrawer(), screen_shape, map_editor)
    ui_layer = ui_layer_maker.make(exit_was_pressed.invoke)

    yield language.get_sprite_loading_message()
    on_board_sprites_drawer = OnBoardSpritesDrawer.make(camera.orientation)
    draw, figures_drawer = DrawMaker().make(screen_shape, on_board_sprites_drawer, session.board, cells_change_observer)

    camera_assistant = CameraAssistant.make(camera)
    layers = [
        ui_layer,
        Layer(MapEditorBoardDrawableLayer(draw, hovered_cell_getter, camera_assistant), board_layer),
        Layer(WholeScreenDrawableLayer(draw), null_layer)
    ]

    input_state = InputState.make(window)
    scene = MapEditorScene.make(camera_mover, camera_orientation, screenshot_saver, input_state, layers)

    def on_exit_was_pressed() -> None:
        on_turn_start(session)
        GameSessionSaver(session).save(EDIT_MAP_FILE)
        scene.on_to_main_menu_was_pressed()

    exit_was_pressed.subscribe(on_exit_was_pressed)

    yield scene
