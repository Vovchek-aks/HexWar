from attrs import define

from appearance.game_engine import make_game_engine
from core.game_session import test_map
from mathematics.vector import Vector2Int
import core.protocols as proto

SCREEN_SHAPE = Vector2Int(1280, 720)
UPS = 60
CAPTION = "HexWar"
BOARD_SIZE = 20


@define
class FakeGameSession(proto.GameSession):
    _session: proto.GameSession

    @property
    def master(self) -> proto.Master:
        return self._session.master

    @property
    def figures_budget(self) -> proto.FiguresRelocationBudget:
        return self._session.figures_budget

    @property
    def board(self) -> proto.Board:
        return self._session.board

    def make(self, move: proto.ValidMove) -> None:
        move.move.execute(self._session)

    def change_session(self, session: proto.GameSession) -> None:
        self._session = session


class Shit(Exception):
    ...


def main() -> None:
    fake_session = FakeGameSession(test_map(board_size=BOARD_SIZE))
    engine, user_inputer = make_game_engine(CAPTION, UPS, SCREEN_SHAPE, fake_session)

    fake_session.master.turn_has_passed.subscribe(lambda player: _try_reboot(fake_session, player))

    with engine:
        engine.run()


def _is_end(board: proto.Board, player: proto.Player) -> bool:
    cells = board.cells
    return cells == cells.with_owner(player)


def _try_reboot(fake_session: FakeGameSession, player: proto.Player) -> None:
    if _is_end(fake_session.board, player):
        raise Shit


if __name__ == '__main__':
    while True:
        try:
            main()
        except Shit:
            pass
