from typing import Iterator, Callable

from appearance.UI.drawer import UiDrawer
from appearance.UI.player_selection_ui_layer_maker import PlayersSelectionUiLayerMaker
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
from appearance.input.players_selector import PlayersSelector
from appearance.input.screenshot_saver import ScreenshotSaver
from appearance.input.under_cursor_cell_getter import UnderCursorCellGetter
from appearance.language import Language
from appearance.layer import Layer
from appearance.scenes.players_selection import PlayersSelectionScene
from core.cells_changes_observer import CellsChangesObserver
from core.game_session import GameSession
from core.by_game_rules_session_changer import ByGameRulesSessionChanger
from mathematics.vector import Vector2Int
from observer import Event
from appearance.game_engine.game_engine_arc.window import Window
import appearance.protocols as proto
from statuses import Status


def load_players_selection(screen_shape: Vector2Int,
                           make_game_scene_loading: Callable[[GameSession], proto.Scene],
                           make_main_menu_scene_loading: Callable[[], proto.Scene],
                           make_game_session: Callable[[], GameSession],
                           window: Window) -> Iterator[proto.Scene | Status]:
    language = Language.from_meta()

    yield language.get_map_loading_message()
    session = make_game_session()

    yield language.get_intermediate_preparing_message()
    screenshot_saver = ScreenshotSaver()

    camera_orientation = CameraOrientation.for_board(session.board)
    camera_mover = CameraMover(camera_orientation)
    camera = CachedCamera.make(Camera(screen_shape.as_vector2, ReadonlyCameraOrientation(camera_orientation)))

    hovered_cell_getter = UnderCursorCellGetter(camera, session.board)

    board_layer = BoardLayer(hovered_cell_getter)
    null_layer = WholeScreenLayer()

    button_press_action_happened = Event[ButtonPressAction, None]()
    actions_reader = InputActionsReader.make(board_layer,
                                             null_layer,
                                             button_press_action_happened.subscriber)

    input_state = InputState.make(window)
    cells_change_observer = CellsChangesObserver.make([], [])
    players_selector = PlayersSelector.make(session, actions_reader)

    yield language.get_ui_making_message()
    exit_was_pressed = Event[None]()
    play_was_pressed = Event[None]()
    ui_layer_maker = PlayersSelectionUiLayerMaker(UiDrawer(), screen_shape)
    ui_layer = ui_layer_maker.make(exit_was_pressed.invoke,
                                   play_was_pressed.invoke,
                                   players_selector.selected_players_were_changed)

    yield language.get_sprite_loading_message()
    on_board_sprites_drawer = OnBoardSpritesDrawer.make(camera.orientation)
    draw, _, board_drawer = DrawMaker().make(screen_shape,
                                             on_board_sprites_drawer,
                                             session.board,
                                             cells_change_observer)

    camera_assistant = CameraAssistant.make(camera)
    layers = [
        ui_layer,
        Layer(MapEditorBoardDrawableLayer(draw, hovered_cell_getter, camera_assistant), board_layer),
        Layer(WholeScreenDrawableLayer(draw), null_layer)
    ]
    scene = PlayersSelectionScene.make(camera_mover, camera_orientation, screenshot_saver, input_state, layers)

    def on_play_was_pressed() -> None:
        if not players_selector.has_selected:
            return

        new_session = GameSession(players_selector.make_master(),
                                  session.board,
                                  session.figures_budget,
                                  session.pulling_connections,
                                  session.cells,
                                  session.figures)

        ByGameRulesSessionChanger(new_session, board_drawer.not_updating_cells, lambda _: None).on_turn_start()
        scene.switch_to(make_game_scene_loading(new_session))

    play_was_pressed.subscribe(on_play_was_pressed)
    exit_was_pressed.subscribe(lambda: scene.switch_to(make_main_menu_scene_loading()))

    yield scene
