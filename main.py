import pygame as pg

from appearance.graphics import colors
from appearance.input.selected_cell_getter import SelectedCellGetter
from events import Events
from core.board import Board
from core.cell import Cell
from core.player import Player
from appearance.graphics.camera.camera import Camera
from appearance.input.camera_mover import CameraMover
from appearance.graphics.camera.camera_orientation import CameraOrientation
from appearance.graphics.drawer import Draw
from mathematics.vector import Vector2Int
import core.figures.figures as fig
from statuses import MISSING

SCREEN_SHAPE = Vector2Int(1080, 720)
UPS = 120


def main():
    pg.init()
    screen = pg.display.set_mode(SCREEN_SHAPE.tuple)
    pg.display.set_caption("HexWar")
    clock = pg.time.Clock()

    player1 = Player(colors.PLAYER_RED)
    player2 = Player(colors.PLAYER_BLUED)
    player3 = Player(colors.PLAYER_GREEN)
    player4 = Player(colors.PLAYER_YELLOW)
    board = Board.from_maker(Vector2Int.ones() * 20,
                             lambda coord: Cell((player2 if coord.y < 8 else player3)
                                                if coord.x > 6 else (player1 if coord.y < 12 else player4),
                                                fig.Empty()))

    camera_orientation = CameraOrientation.starter()
    camera_mover = CameraMover(camera_orientation)
    camera = Camera(SCREEN_SHAPE, camera_orientation)

    selected_getter = SelectedCellGetter(camera, board)

    draw = Draw(screen, camera, board)

    dt = 1 / UPS
    while not need_to_stop(events := Events(pg.event.get())):
        keys = pg.key.get_pressed()
        mouse_position = pg.Vector2(*pg.mouse.get_pos())

        camera_mover.update(events, keys, dt)

        draw.background()
        draw.board()

        if (selected_coord := selected_getter.get_coord(mouse_position)) is not MISSING:
            draw.highlighted(selected_coord)

        pg.display.flip()
        dt = clock.tick(UPS) / 1_000

        pg.display.set_caption(f"HexWar {1 / dt:.0f}FPS")

    pg.quit()


def need_to_stop(events: Events) -> bool:
    return pg.QUIT in events


if __name__ == '__main__':
    main()
