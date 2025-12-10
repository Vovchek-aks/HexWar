import random

from attrs import frozen

from core import protocols as proto
from core.figures import figures as fig
from core.moves.creation import Creation
from core.moves.relocations import Relocation, Assault
from observer import Event
from statuses import Status, MISSING, INVALID


@frozen
class BotIgor(proto.Bot):
    @classmethod
    def make(cls, session: proto.GameSession, event_to_call: Event[proto.ValidMove, None]) -> "BotIgor":
        return cls(session,
                   session.master.current_player,
                   session.board,
                   session.figures_budget,
                   event_to_call)

    _session: proto.GameSession
    _player: proto.Player
    _board: proto.Board
    _figures_budget: proto.FiguresRelocationBudget
    _move_was_inputted: Event[proto.ValidMove, None]

    def update(self) -> bool:
        did_pulled = self.try_pull_forces_to_front()
        did_advanced = self.try_advance_forces()

        cells_count = self.count_of(fig.Figure)
        town_count = self.count_of(fig.Town)

        if town_count < cells_count * .1 or town_count < 3:
            have_build = self.try_create(fig.Town)
        else:
            have_build = self.try_create(fig.Infantry)

        if not have_build:
            have_build = self.try_create(fig.Town)

        return not any((
            did_advanced,
            did_pulled,
            have_build,
        ))

    def get_cell_for(self, figure: type[fig.Figure]) -> proto.Cell | Status:
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

    def get_target_enemy(self, cell: proto.Cell) -> proto.Cell | Status:
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

    def get_target_front_cell(self, cell: proto.Cell) -> proto.Cell | Status:
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

    def try_pull_forces_to_front(self) -> bool:
        all_armed = (self._board.cells
                     .with_owner(self._player)
                     .with_figure(fig.Infantry | fig.Motorization | fig.Tank))
        if not all_armed:
            return False

        front = all_armed.at_front(self._board)
        if not front:
            return False

        back = all_armed - front
        some_move_was_valid = False
        for cell in back:
            if (target := self.get_target_front_cell(cell)) is MISSING:
                continue

            move = Relocation(self._board.coordinates_of(cell),
                              self._board.coordinates_of(target))
            if (valid_move := move.validate(self._session)) is INVALID:
                continue

            self._move_was_inputted.invoke(valid_move)
            some_move_was_valid = True

        return some_move_was_valid

    def try_advance_forces(self) -> bool:
        all_armed = (self._board.cells
                     .with_owner(self._player)
                     .with_figure(fig.Infantry | fig.Motorization | fig.Tank))
        if not all_armed:
            return False

        armed_front = all_armed.at_front(self._board)
        if not armed_front:
            return False

        some_move_was_valid = False
        for cell in armed_front:
            if (target := self.get_target_enemy(cell)) is MISSING:
                continue

            move = Assault(self._board.coordinates_of(cell),
                           self._board.coordinates_of(target))
            if (valid_move := move.validate(self._session)) is INVALID:
                continue

            self._move_was_inputted.invoke(valid_move)
            some_move_was_valid = True

        return some_move_was_valid

    def can_create(self, figure: type[fig.Figure], cell: proto.Cell) -> bool:
        if not cell.is_empty:
            return False

        if not self._player.resources.can_take(figure.FLAGS.get(proto.Creatable).cost):
            return False

        return Creation(fig.Town, self._board.coordinates_of(cell)).validate(self._session) is not INVALID

    def create(self, figure: type[fig.Figure], cell: proto.Cell) -> proto.ValidMove:
        assert self.can_create(figure, cell)

        move = Creation(figure, self._board.coordinates_of(cell))
        return move.validate(self._session)

    def try_create(self, figure: type[fig.Figure]) -> bool:
        if (cell := self.get_cell_for(figure)) is MISSING:
            return False

        if not self.can_create(figure, cell):
            return False

        self._move_was_inputted.invoke(self.create(figure, cell))
        return True

    def count_of(self, figure: type[fig.Figure]) -> int:
        return len(self._board.cells.with_owner(self._player).with_figure(figure).all())
