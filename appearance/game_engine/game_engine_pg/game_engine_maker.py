import pygame as pg

from appearance.UI.drawer import UiDrawer
from appearance.UI.game_ui_layer_maker import GameUiLayerMaker
from appearance.game_engine.game_engine_pg.game_engine import GameEngine
from appearance.game_engine.game_engine_pg.updater import Updater
from appearance.graphics.layer_drawers.board_drawable_layer import BoardDrawableLayer
from appearance.graphics.layer_drawers.whole_screen_drawable_layer import WholeScreenDrawableLayer
from appearance.graphics.sprites import SpritesLoader
from appearance.input.mouse_movement_observer import MouseMovementObserver
from appearance.input.moves_inputer.input_actions import ButtonPressAction
from appearance.input.screenshot_saver import ScreenshotSaver
from appearance.layer import Layer
from core.player.player_moves_maker import player_moves_maker
from mathematics.vector import Vector2Int, Vector2
from appearance.graphics.camera.camera import Camera
from appearance.graphics.camera.camera_orientation import CameraOrientation, ReadonlyCameraOrientation
from appearance.graphics.draw import Draw, DrawMaker
from appearance.input.cell_selector import CellSelector
from appearance.input.clicks_catcher.layers.board_layer import BoardLayer
from appearance.input.clicks_catcher.layers.whole_screen_layer import WholeScreenLayer
from appearance.input.moves_inputer import MovesInputer
from appearance.input.moves_inputer.actions_reader import InputActionsReader
from appearance.input.under_cursor_cell_getter import UnderCursorCellGetter
from core.moves_maker import MovesMaker
from appearance.game_engine.game_engine_pg.events import UpdatableEvents
from appearance.game_engine.game_engine_pg.frame_drawer import FrameDrawer
from appearance.game_engine.game_engine_pg.timer import Timer
from appearance.input.camera_mover import CameraMover
from core.player.inputers.event_player_inputer import EventPlayerInputerBuilder, EventPlayerInputer
from core.protocols import GameSession
from observer import Event


def make_game_engine(caption: str,
                     ups: int,
                     screen_shape: Vector2Int,
                     session: GameSession) -> tuple[GameEngine, EventPlayerInputer]:
    pg.init()
    screen = pg.display.set_mode(screen_shape.tuple)
    pg.display.set_caption(caption)

    _blit_loading_screen(screen, screen_shape)

    timer = Timer.make(ups)

    screenshot_saver = ScreenshotSaver(screen)

    camera_orientation = CameraOrientation.starter()
    camera_mover = CameraMover(camera_orientation)
    camera = Camera(screen_shape, ReadonlyCameraOrientation(camera_orientation))

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
    ui_layer = (GameUiLayerMaker(UiDrawer(screen),
                                 screen_shape,
                                 session,
                                 cell_selector,
                                 mouse_movement_observer,
                                 button_press_action_happened,
                                 moves_maker,
                                 actions_reader)
                .make(user_inputer_builder))

    draw = DrawMaker(Draw).make(screen, camera, session.board, )

    layers = [
        ui_layer,
        Layer(BoardDrawableLayer(draw, hovered_cell_getter, cell_selector), board_layer),
        Layer(WholeScreenDrawableLayer(draw), null_layer)
    ]

    updater = Updater.make(camera_mover, screenshot_saver, mouse_movement_observer, layers,
                           player_moves_maker(session, moves_maker))
    drawer = FrameDrawer.make(layers)

    return (GameEngine(caption, timer, drawer, updater, UpdatableEvents.new()),
            user_inputer_builder.build())


def _blit_loading_screen(screen: pg.Surface, screen_shape: Vector2Int) -> None:
    loading = SpritesLoader.from_meta().load_loading_screen()
    loading = loading.reshape(screen_shape)
    loading.blit_on(screen, Vector2.zero())
    pg.display.flip()
