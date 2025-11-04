import pygame as pg

from appearance.game_engine.game_engine_pg.game_engine import GameEngine
from mathematics.vector import Vector2Int
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
from appearance.input.clicks_catcher import ClicksCatcher
from core.protocols import GameSession


def make_game_engine(caption: str, ups: int, screen_shape: Vector2Int, session: GameSession) -> GameEngine:
    pg.init()
    screen = pg.display.set_mode(screen_shape.tuple)
    pg.display.set_caption(caption)

    timer = Timer.make(ups)

    camera_orientation = CameraOrientation.starter()
    camera_mover = CameraMover(camera_orientation)
    camera = Camera(screen_shape, ReadonlyCameraOrientation(camera_orientation))

    hovered_cell_getter = UnderCursorCellGetter(camera, session.board)

    board_layer = BoardLayer(hovered_cell_getter)
    null_layer = WholeScreenLayer()
    clicks_catcher = ClicksCatcher([board_layer, null_layer])

    actions_reader = InputActionsReader.make(board_layer, null_layer)

    moves_maker = MovesMaker(session)
    cell_selector = CellSelector.make(actions_reader, moves_maker)

    moves_inputer = MovesInputer.make(actions_reader, session.board, cell_selector)
    moves_inputer.move_was_raed.subscribe(moves_maker.make)

    draw = DrawMaker(Draw).make(screen, camera, session.board)

    drawer = FrameDrawer(draw, hovered_cell_getter, cell_selector)

    return GameEngine(caption, timer, drawer, camera_mover, clicks_catcher, UpdatableEvents.new())
