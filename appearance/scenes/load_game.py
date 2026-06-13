from typing import Callable, Iterator

from attrs import frozen

from appearance.UI.drawer import UiDrawer
from appearance.UI.game_ui_layer_maker import GameUiLayerMaker
from appearance.UI.pause_menu_ui_layer_maker import PauseMenuUiLayerMaker
from appearance.animations.to_target_orientation_camera_mover import ToTargetOrientationCameraMover
from appearance.animations.turn_pass_animator import TurnPassAnimator
from appearance.audio.music.music_player import MusicPlayer, NoMusicPlayer
from appearance.audio.sound.figure_selection.figures_sounds import FiguresSounds
from appearance.audio.sound.figure_selection.on_figure_was_clicked_sound_player import OnFigureWasClickedSoundPlayer
from appearance.camera_mover import CameraMover
from appearance.game_engine.game_engine_arc.frame_drawer import FrameDrawer
from appearance.game_engine.game_engine_arc.in_game_time import InGameTime
from appearance.game_engine.game_engine_arc.input_state import InputState
from appearance.game_engine.game_engine_arc.updater import Updater
from appearance.animations.moves_animator import MovesAnimator
from appearance.animations.moves_animators_switcher import MovesAnimatorsSwitcher
from appearance.graphics.camera.camera import CachedCamera, Camera
from appearance.graphics.camera.camera_orientation import CameraOrientation, ReadonlyCameraOrientation
from appearance.graphics.draw import DrawMaker
from appearance.graphics.draw.drawers.drawers_arc.background_drawer import BackgroundDrawer
from appearance.graphics.draw.drawers.drawers_arc.bord_drawer.annexation_hatching_map_updater import \
    AnnexationHatchingMapUpdater
from appearance.graphics.draw.drawers.drawers_arc.bord_drawer.hatching_map import HatchingMap
from appearance.graphics.draw.drawers.drawers_arc.camera_assistant_arc import CameraAssistant
from appearance.graphics.draw.drawers.drawers_arc.on_board_sprites_drawer import OnBoardSpritesDrawer
from appearance.graphics.layer_drawers.board_drawable_layer import BoardDrawableLayer
from appearance.graphics.layer_drawers.whole_screen_drawable_layer import WholeScreenDrawableLayer
from appearance.input.keyboard_camera_mover import KeyboardCameraMover
from appearance.input.cell_selector import CellSelector
from appearance.input.clicks_catcher.layers.board_layer import BoardLayer
from appearance.input.clicks_catcher.layers.whole_screen_layer import WholeScreenLayer
from appearance.input.mouse_movement_observer import MouseMovementObserver
from appearance.input.moves_inputer import MovesInputer
from appearance.input.moves_inputer.actions_reader import InputActionsReader
from appearance.input.moves_inputer.input_actions import ButtonPressAction
from appearance.input.moves_inputer.multiple_relocations_reader import MultipleRelocationsReader
from appearance.input.pause_menu_opener import PauseMenuOpener
from appearance.input.screenshot_saver import ScreenshotSaver
from appearance.input.under_cursor_cell_getter import UnderCursorCellGetter
from appearance.language import Language
from appearance.layer import Layer
from appearance.scenes.game_scene import GameScene
from appearance.scenes.game_with_pause_scene import GameWithPauseScene
from appearance.scenes.multibot_scene import MultibotScene
from appearance.scenes.pause_menu import PauseMenu
from appearance.settings import Settings
from core.annexation_map.annexation_map import AnnexationMap
from core.annexation_map.annexation_map_updater import AnnexationMapUpdater
from core.cells_changes_observer import CellsChangesObserver
from core.player.inputers.wants_to_be_event_player_inputer import WantsToBeEventPlayerInputer
from game_session_saver import GameSessionSaver, SAVE_FILE
from core.moves_maker import MovesMaker
from core.player.inputers.event_player_inputer import EventPlayerInputerBuilder
from core.player.players_moves_maker import players_moves_maker
from core.by_game_rules_session_changer import ByGameRulesSessionChanger
from core.protocols import GameSession, Player
from mathematics.vector import Vector2Int
from observer import Event
from appearance.game_engine.game_engine_arc.window import Window
import appearance.protocols as proto
from statuses import Status
from appearance.graphics.colors import PAUSE_MENU_BACKGROUND


def load_game(window: Window,
              make_session: Callable[[], GameSession],
              make_next_scene_loading: Callable[[], proto.Scene],
              *,
              is_multibot: bool = False) -> Iterator[proto.Scene | Status]:
    screen_shape = Settings.open().screen_shape
    language = Language.from_meta()

    yield language.get_map_loading_message()
    session = make_session()

    yield language.get_intermediate_preparing_message()
    screenshot_saver = ScreenshotSaver()

    camera_orientation = CameraOrientation.for_board(session.board)
    camera = CachedCamera.make(Camera(screen_shape.as_vector2, ReadonlyCameraOrientation(camera_orientation)))
    keyboard_camera_mover = KeyboardCameraMover(camera_orientation)
    to_target_camera_mover = ToTargetOrientationCameraMover(camera_orientation)
    camera_mover = CameraMover(keyboard_camera_mover, to_target_camera_mover)

    hovered_cell_getter = UnderCursorCellGetter(camera, session.board)

    board_layer = BoardLayer(hovered_cell_getter)
    null_layer = WholeScreenLayer()

    button_press_action_happened = Event[ButtonPressAction, None]()
    actions_reader = InputActionsReader.make(board_layer,
                                             null_layer,
                                             button_press_action_happened.subscriber)

    moves_maker = MovesMaker(session)

    cell_changed_figure = Event[Vector2Int, None]()
    cell_changed_owner = Event[Vector2Int, None]()
    session.figures.figure_was_added_at.subscribe(lambda _, coord: cell_changed_figure.invoke(coord))
    session.figures.figure_was_removed.subscribe(lambda _, coord: cell_changed_figure.invoke(coord))
    session.figures.figure_was_converted.subscribe(lambda _, __, coord: cell_changed_figure.invoke(coord))
    session.figures.figure_was_moved.subscribe(lambda _, coord, __: cell_changed_figure.invoke(coord))
    session.figures.figure_was_moved.subscribe(lambda _, __, coord: cell_changed_figure.invoke(coord))
    cells_change_observer = CellsChangesObserver.make([moves_maker.cell_changed_owner, cell_changed_owner.subscriber],
                                                      [cell_changed_figure.subscriber])

    cells_change_observer.cell_changed_figure.subscribe(lambda coord: session.cells.update(session.board[coord]))
    cells_change_observer.cell_changed_owner.subscribe(lambda coord: session.cells.update(session.board[coord]))

    figures_sounds = FiguresSounds.load()
    OnFigureWasClickedSoundPlayer.make(session, figures_sounds, actions_reader)
    music_player = MusicPlayer.load()  # if not is_multibot else NoMusicPlayer()

    input_state = InputState.make(window)

    cell_selector = CellSelector.make(actions_reader, moves_maker, session.master)
    multiple_relocations_reader = MultipleRelocationsReader(session, cell_selector, input_state)
    moves_inputer = MovesInputer.make(actions_reader, multiple_relocations_reader, session, cell_selector)

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
    ui_layer = (game_ui_layer_maker.make_for_multibot()
                if is_multibot else
                game_ui_layer_maker.make(end_turn_button_was_clicked.invoke))

    yield language.get_sprite_loading_message()
    on_board_sprites_drawer = OnBoardSpritesDrawer.make(camera.orientation)
    hatching_map = HatchingMap()
    draw, figures_drawer, board_drawer = DrawMaker().make(screen_shape,
                                                          on_board_sprites_drawer,
                                                          session.board,
                                                          hatching_map,
                                                          cells_change_observer)

    camera_assistant = CameraAssistant.make(camera)
    layers = [
        ui_layer,
        Layer(BoardDrawableLayer(session, draw, hovered_cell_getter, cell_selector, camera_assistant,
                                 multiple_relocations_reader, actions_reader), board_layer),
        Layer(WholeScreenDrawableLayer(draw), null_layer)
    ]

    in_game_time = InGameTime()
    players_moves_animations = MovesAnimator.make(on_board_sprites_drawer, figures_drawer, camera, session,
                                                  in_game_time)
    bots_moves_animations = MovesAnimator.make(on_board_sprites_drawer, figures_drawer, camera, session,
                                               in_game_time, speed_multiplier=float('inf'), volume_multiplier=.2)
    # bots_moves_animations = MovesAnimator.make(on_board_sprites_drawer, figures_drawer, camera, session,
    #                                            in_game_time, speed_multiplier=3, volume_multiplier=.2)
    animators_switcher = MovesAnimatorsSwitcher.make(session.master, players_moves_animations, bots_moves_animations)

    annexation_map_updater = AnnexationMapUpdater.make(session, moves_maker, AnnexationMap(session))
    by_game_rules_session_changer = ByGameRulesSessionChanger(session,
                                                              annexation_map_updater,
                                                              board_drawer.not_updating_cells,
                                                              cell_changed_owner.invoke)
    hatching_map_updater = AnnexationHatchingMapUpdater.make(session, hatching_map, board_drawer,
                                                             annexation_map_updater)

    turn_pass_animator = TurnPassAnimator(camera, to_target_camera_mover, in_game_time, session,
                                          hatching_map_updater, annexation_map_updater)

    updater = Updater.make(camera_mover, camera_orientation, screenshot_saver, pause_menu_opener,
                           mouse_movement_observer, layers,
                           players_moves_maker(session, moves_maker, by_game_rules_session_changer,
                                               lambda move: animators_switcher.get().get_animation(move),
                                               (turn_pass_animator.start_for_multibot
                                                if is_multibot else
                                                turn_pass_animator.start_for_game),
                                               (turn_pass_animator.end_for_multibot
                                                if is_multibot else
                                                turn_pass_animator.end_for_game),
                                               ),
                           in_game_time,
                           [
                               annexation_map_updater.update,
                               hatching_map_updater.update,
                               music_player.update,
                           ])
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

        def on_player_turn_started(player: Player) -> None:
            ratio_to_win = .7
            if max(session.cells.get_territories_and_production_ratios_of(player)) >= ratio_to_win:
                scene.on_reload(make_next_scene_loading())

        session.master.turn_had_started.subscribe(on_player_turn_started)
        by_game_rules_session_changer.on_turn_start()
    else:
        pause_menu = PauseMenu.make(screenshot_saver, input_state, pause_menu_layers, pause_menu_opener)
        scene = GameWithPauseScene(game, pause_menu)

        user_inputer_builder = EventPlayerInputerBuilder()
        user_inputer_builder.set_move_was_read(moves_inputer.move_was_read)
        user_inputer_builder.set_need_to_end_turn(end_turn_button_was_clicked.subscriber)

        end_turn_button_was_clicked.subscribe(lambda: GameSessionSaver(session).save(SAVE_FILE))

        for player in session.master.players:
            if not isinstance(player.inputer, WantsToBeEventPlayerInputer):
                continue
            player.change_inputer(user_inputer_builder.build())

        animators_switcher.switch(session.master.current_player)

        pause_menu_open_requested.subscribe(scene.on_pause_menu_toggle_requested)
        continue_was_pressed.subscribe(scene.on_pause_menu_toggle_requested)
        to_main_menu_was_pressed.subscribe(lambda: scene.on_to_main_menu_was_pressed(make_next_scene_loading()))
        to_main_menu_was_pressed.subscribe(lambda: GameSessionSaver(session).save(SAVE_FILE))
        to_main_menu_was_pressed.subscribe(lambda: music_player.stop())

    yield scene


@frozen
class Draw:
    _background_drawer: BackgroundDrawer

    def background(self) -> None:
        self._background_drawer.draw_background()
