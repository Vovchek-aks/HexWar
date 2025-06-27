import pygame as pg

from gameplay.board import Board
from gameplay.cell import Cell
from gameplay.player import Player
from graphics.camera import Camera
from graphics.drawer import Draw
from vector import Vector2Int
import gameplay.figures.figures as fig

SHAPE = 1080, 720
UPS = 60

BACKGROUND = pg.Color(66, 133, 180).lerp(0, .3)


def main():
    pg.init()
    screen = pg.display.set_mode(SHAPE)
    pg.display.set_caption("HexWar")
    clock = pg.time.Clock()

    player1 = Player(pg.Color(175, 43, 30))
    player2 = Player(pg.Color(18, 47, 170))
    player3 = Player(pg.Color(46, 139, 87))
    player4 = Player(pg.Color(255, 186, 0))
    board = Board.from_maker(Vector2Int.ones() * 10,
                             lambda coord: Cell((player2 if coord.y < 4 else player3)
                                                if coord.x > 3 else (player1 if coord.y < 6 else player4), fig.Empty()))
    camera = Camera()

    draw = Draw(screen, camera, board)

    dt = 1 / UPS
    while not need_to_stop(events := list(pg.event.get())):
        screen.fill(BACKGROUND)

        draw.board()
        pg.display.flip()
        dt = clock.tick(UPS) / 1_000

        pg.display.set_caption(f"HexWar {1 / dt:.0f}")

    pg.quit()


def need_to_stop(events):
    for event in events:
        if event.type == pg.QUIT:
            return True

    return False


if __name__ == '__main__':
    main()
