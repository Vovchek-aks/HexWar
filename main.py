import pygame as pg

from events import Events
from core.board import Board
from core.cell import Cell
from core.player import Player
from appearance.graphics.camera.camera import Camera
from appearance.input.camera_mover import CameraMover
from appearance.graphics.camera.camera_orientation import CameraOrientation
from appearance.graphics.drawer import Draw
from vector import Vector2Int
import core.figures.figures as fig

SHAPE = Vector2Int(1080, 720)
UPS = 60

BACKGROUND = pg.Color(66, 133, 180).lerp(0, .3)


def main():
    pg.init()
    screen = pg.display.set_mode(SHAPE.tuple)
    pg.display.set_caption("HexWar")
    clock = pg.time.Clock()

    player1 = Player(pg.Color(175, 43, 30))
    player2 = Player(pg.Color(18, 47, 170))
    player3 = Player(pg.Color(46, 139, 87))
    player4 = Player(pg.Color(255, 186, 0))
    board = Board.from_maker(Vector2Int.ones() * 20,
                             lambda coord: Cell((player2 if coord.y < 8 else player3)
                                                if coord.x > 6 else (player1 if coord.y < 12 else player4),
                                                fig.Empty()))

    camera_orientation = CameraOrientation.starter()
    camera_mover = CameraMover(camera_orientation)
    camera = Camera(SHAPE, camera_orientation)

    draw = Draw(screen, camera, board)

    dt = 1 / UPS
    while not need_to_stop(events := Events(pg.event.get())):
        camera_mover.update(events, pg.key.get_pressed(), dt)

        screen.fill(BACKGROUND)
        draw.board()

        pg.display.flip()
        dt = clock.tick(UPS) / 1_000

        pg.display.set_caption(f"HexWar {1 / dt:.0f}FPS")

    pg.quit()


def need_to_stop(events: Events) -> bool:
    return pg.QUIT in events


if __name__ == '__main__':
    main()
