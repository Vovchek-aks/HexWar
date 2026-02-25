from typing import Callable, Iterator

from attrs import frozen

from appearance.UI.drawer import UiDrawer
from appearance.UI.game_ui_layer_maker import GameUiLayerMaker
from appearance.UI.pause_menu_ui_layer_maker import PauseMenuUiLayerMaker
from appearance.game_engine.game_engine_arc.frame_drawer import FrameDrawer
from appearance.game_engine.game_engine_arc.in_game_time import InGameTime
from appearance.game_engine.game_engine_arc.input_state import InputState
from appearance.game_engine.game_engine_arc.updater import Updater
from appearance.graphics.animations.moves_animator import MovesAnimator
from appearance.graphics.animations.moves_animators_switcher import MovesAnimatorsSwitcher
from appearance.graphics.camera.camera import CachedCamera, Camera
from appearance.graphics.camera.camera_orientation import CameraOrientation, ReadonlyCameraOrientation
from appearance.graphics.draw import DrawMaker
from appearance.graphics.draw.drawers.drawers_arc.background_drawer import BackgroundDrawer
from appearance.graphics.draw.drawers.drawers_arc.camera_assistant_arc import CameraAssistant
from appearance.graphics.draw.drawers.drawers_arc.on_board_sprites_drawer import OnBoardSpritesDrawer
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
from appearance.scenes.game_with_pause_scene import GameWithPauseScene
from appearance.scenes.multibot_scene import MultibotScene
from appearance.scenes.pause_menu import PauseMenu
from core.cells_changes_observer import CellsChangesObserver
from core.figures.figure import Town
from core.player.inputers.wants_to_be_event_player_inputer import WantsToBeEventPlayerInputer
from game_session_saver import GameSessionSaver
from core.moves_maker import MovesMaker
from core.player.inputers.event_player_inputer import EventPlayerInputerBuilder
from core.player.players_moves_maker import players_moves_maker
from core.protocols import GameSession, Player
from mathematics.vector import Vector2Int
from observer import Event
from appearance.game_engine.game_engine_arc.window import Window
import appearance.protocols as proto
from statuses import Status
from appearance.graphics.colors import PAUSE_MENU_BACKGROUND


def load_game(screen_shape: Vector2Int,
              window: Window,
              make_session: Callable[[], GameSession],
              make_next_scene_loading: Callable[[], proto.Scene],
              *,
              is_multibot: bool = False) -> Iterator[proto.Scene | Status]:
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

    pause_menu_open_requested = Event[None]()
    pause_menu_opener = PauseMenuOpener(pause_menu_open_requested.invoke)

    mouse_movement_observer = MouseMovementObserver()

    yield language.get_ui_making_message()
    end_turn_button_was_clicked = Event[None]()
    game_ui_layer_maker = GameUiLayerMaker(UiDrawer(),
                                           screen_shape,
                                           session,
                                           cell_selector,
                                           mouse_movement_observer,
                                           button_press_action_happened,
                                           moves_maker,
                                           actions_reader)
    ui_layer = (game_ui_layer_maker.make_multibot()
                if is_multibot else
                game_ui_layer_maker.make(end_turn_button_was_clicked.invoke))

    yield language.get_sprite_loading_message()
    on_board_sprites_drawer = OnBoardSpritesDrawer.make(camera.orientation)
    draw, figures_drawer = DrawMaker().make(screen_shape, on_board_sprites_drawer, session.board, cells_change_observer)

    camera_assistant = CameraAssistant.make(camera)
    layers = [
        ui_layer,
        Layer(BoardDrawableLayer(draw, hovered_cell_getter, cell_selector, camera_assistant), board_layer),
        Layer(WholeScreenDrawableLayer(draw), null_layer)
    ]

    in_game_time = InGameTime()
    players_moves_animations = MovesAnimator.make(on_board_sprites_drawer, figures_drawer, camera, session,
                                                  in_game_time)
    bots_moves_animations = MovesAnimator.make(on_board_sprites_drawer, figures_drawer, camera, session,
                                               in_game_time, speed_multiplier=3)
    # speed_multiplier=float('inf'))
    animators_switcher = MovesAnimatorsSwitcher.make(session.master, players_moves_animations, bots_moves_animations)

    updater = Updater.make(camera_mover, camera_orientation, screenshot_saver, pause_menu_opener,
                           mouse_movement_observer, layers,
                           players_moves_maker(session, moves_maker,
                                               lambda move: animators_switcher.get().get_animation(move)),
                           in_game_time)
    drawer = FrameDrawer.make(layers)

    continue_was_pressed = Event[None]()
    to_main_menu_was_pressed = Event[None]()
    pause_menu_layers = [
        PauseMenuUiLayerMaker(UiDrawer(), screen_shape).make(continue_was_pressed.invoke,
                                                             to_main_menu_was_pressed.invoke),
        Layer(WholeScreenDrawableLayer(Draw(BackgroundDrawer(screen_shape, PAUSE_MENU_BACKGROUND))), null_layer)
    ]

    game = GameScene(drawer, updater, InputState.make(window))
    if is_multibot:
        scene = MultibotScene(game)

        def on_player_turn_ended(player: Player) -> None:
            towns = session.cells.with_figure(Town)
            player_towns = session.cells.with_owner(player) & towns
            if len(player_towns.all()) > len(towns.all()) * .9:
                scene.on_reload(make_next_scene_loading())

        session.master.turn_has_passed.subscribe(on_player_turn_ended)
    else:
        pause_menu = PauseMenu.make(screenshot_saver, InputState.make(window), pause_menu_layers, pause_menu_opener)
        scene = GameWithPauseScene(game, pause_menu)

        user_inputer_builder = EventPlayerInputerBuilder()
        user_inputer_builder.set_move_was_read(moves_inputer.move_was_raed)
        user_inputer_builder.set_need_to_end_turn(end_turn_button_was_clicked.subscriber)

        for player in session.master.players:
            if not isinstance(player.inputer, WantsToBeEventPlayerInputer):
                continue
            player.change_inputer(user_inputer_builder.build())

        animators_switcher.switch(session.master.current_player)

        pause_menu_open_requested.subscribe(scene.on_pause_menu_toggle_requested)
        continue_was_pressed.subscribe(scene.on_pause_menu_toggle_requested)
        to_main_menu_was_pressed.subscribe(lambda: scene.on_to_main_menu_was_pressed(make_next_scene_loading()))
        to_main_menu_was_pressed.subscribe(lambda: GameSessionSaver(session).save("aboba.json"))

    yield scene


@frozen
class Draw:
    _background_drawer: BackgroundDrawer

    def background(self) -> None:
        self._background_drawer.draw_background()
