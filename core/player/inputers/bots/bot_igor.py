import random

from attrs import define, field

from core import protocols as proto
from core.figures import figures as fig
from core.moves.creation import Creation
from core.moves.relocations import Relocation, Assault
from statuses import Status, MISSING, INVALID


@define
class BotIgor(proto.Bot):
    @classmethod
    def make(cls) -> "BotIgor":
        return cls()

    _session: proto.GameSession | Status = field(init=False, default=MISSING)

    @property
    def _player(self) -> proto.Player:
        assert self._session is not MISSING
        return self._session.master.current_player

    @property
    def _board(self) -> proto.Board:
        assert self._session is not MISSING
        return self._session.board

    @property
    def _figures_budget(self) -> proto.FiguresRelocationBudget:
        assert self._session is not MISSING
        return self._session.figures_budget

    def get_move(self, session: proto.GameSession) -> proto.ValidMove | Status:
        self._session = session

        move = self._try_pull_forces_to_front()
        if move is not MISSING:
            return move

        move = self._try_advance_forces()
        if move is not MISSING:
            return move

        cells_count = self._count_of(fig.Figure)
        town_count = self._count_of(fig.Town)

        move = (self._try_create(fig.Town)
                if town_count < cells_count * .1 or town_count < 3 else
                self._try_create(fig.Infantry))
        if move is not MISSING:
            return move

        move = self._try_create(fig.Town)
        if move is not MISSING:
            return move

        return MISSING

    def _get_cell_for(self, figure: type[fig.Figure]) -> proto.Cell | Status:
        empties = self._board.cells.with_owner(self._player).with_figure(fig.Empty)
        if not empties:
            return MISSING

        front = empties.at_front(self._board)
        back = empties - front

        match figure:
            case fig.Infantry | fig.Bunker:
                candidates = front
            case fig.Town:
                candidates = back or empties
            case _:
                candidates = empties

        if not candidates:
            return MISSING

        cell: proto.Cell = random.choice(list(candidates.all()))
        return cell

    def _get_target_enemy(self, cell: proto.Cell) -> proto.Cell | Status:
        neighbors = self._board.get_neighbors(cell, include_cell=False)
        if not neighbors:
            return MISSING

        targets = neighbors - neighbors.with_owner(self._player)
        if not targets:
            return MISSING

        empty_targets = targets.with_figure(fig.Empty)
        not_empty_targets = targets - empty_targets
        targets = not_empty_targets or empty_targets

        return random.choice(list(targets.all()))

    def _get_target_front_cell(self, cell: proto.Cell) -> proto.Cell | Status:
        all_armed = (self._board.cells
                     .with_owner(self._player)
                     .with_figure(fig.Infantry | fig.Motorization | fig.Tank))
        if not all_armed:
            return MISSING

        front = all_armed.at_front(self._board)
        if not front:
            return MISSING

        target_front_cell = min(front.all(), key=lambda front_cell: (self._board.coordinates_of(cell) -
                                                                     self._board.coordinates_of(front_cell)).length)

        neighbors = (self._board
                     .get_neighbors(cell, include_cell=False)
                     .with_owner(self._player)
                     .with_figure(fig.Empty))
        if not neighbors:
            return MISSING

        target = min(neighbors.all(), key=lambda neighbor: (self._board.coordinates_of(target_front_cell) -
                                                            self._board.coordinates_of(neighbor)).length)

        return target

    def _try_pull_forces_to_front(self) -> proto.ValidMove | Status:
        all_armed = (self._board.cells
                     .with_owner(self._player)
                     .with_figure(fig.Infantry | fig.Motorization | fig.Tank))
        if not all_armed:
            return MISSING

        front = all_armed.at_front(self._board)
        if not front:
            return MISSING

        back = all_armed - front
        for cell in back:
            if (target := self._get_target_front_cell(cell)) is MISSING:
                continue

            move = Relocation(self._board.coordinates_of(cell),
                              self._board.coordinates_of(target))
            if (valid_move := move.validate(self._session)) is not INVALID:
                return valid_move

        return MISSING

    def _try_advance_forces(self) -> proto.ValidMove | Status:
        all_armed = (self._board.cells
                     .with_owner(self._player)
                     .with_figure(fig.Infantry | fig.Motorization | fig.Tank))
        if not all_armed:
            return MISSING

        armed_front = all_armed.at_front(self._board)
        if not armed_front:
            return MISSING

        for cell in armed_front:
            if (target := self._get_target_enemy(cell)) is MISSING:
                continue

            move = Assault(self._board.coordinates_of(cell),
                           self._board.coordinates_of(target))
            if (valid_move := move.validate(self._session)) is not INVALID:
                return valid_move

        return MISSING

    def _can_create(self, figure: type[fig.Figure], cell: proto.Cell) -> bool:
        if not cell.is_empty:
            return False

        if not self._player.resources.can_take(figure.FLAGS.get(proto.Creatable).cost):
            return False

        return Creation(fig.Town, self._board.coordinates_of(cell)).validate(self._session) is not INVALID

    def _create(self, figure: type[fig.Figure], cell: proto.Cell) -> proto.ValidMove:
        assert self._can_create(figure, cell)

        move = Creation(figure, self._board.coordinates_of(cell))
        return move.validate(self._session)

    def _try_create(self, figure: type[fig.Figure]) -> proto.ValidMove | Status:
        if (cell := self._get_cell_for(figure)) is MISSING:
            return MISSING

        if not self._can_create(figure, cell):
            return MISSING

        return self._create(figure, cell)

    def _count_of(self, figure: type[fig.Figure]) -> int:
        return len(self._board.cells.with_owner(self._player).with_figure(figure).all())
