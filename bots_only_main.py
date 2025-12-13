from appearance.game_engine import make_game_engine
from core.game_session import test_map
from mathematics.vector import Vector2Int
import core.protocols as proto

SCREEN_SHAPE = Vector2Int(1280, 720)
UPS = 60
CAPTION = "HexWar"
BOARD_SIZE = 20


class Shit(Exception):
    ...


def main() -> None:
    session = test_map(board_size=BOARD_SIZE, initial_town_ratio=.05)
    engine, user_inputer = make_game_engine(CAPTION, UPS, SCREEN_SHAPE, session)

    session.master.turn_has_passed.subscribe(lambda player: _try_reboot(session, player))

    with engine:
        engine.run()


def _is_end(board: proto.Board, player: proto.Player) -> bool:
    cells = board.cells
    return len(cells.all()) * .8 <= len(cells.with_owner(player).all())


def _try_reboot(fake_session: proto.GameSession, player: proto.Player) -> None:
    if _is_end(fake_session.board, player):
        raise Shit


if __name__ == '__main__':
    while True:
        try:
            main()
        except Shit:
            pass
