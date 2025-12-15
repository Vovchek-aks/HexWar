import random

from attrs import define, field

from core import protocols as proto
from core.cells import Cells
from core.figures import figures as fig
from core.moves.conversion import Conversion
from core.moves.creation import Creation
from core.moves.relocations import Relocation, Assault
from statuses import Status, MISSING, INVALID


@define
class BotIgor(proto.Bot):
    _session: proto.GameSession | Status = field(init=False, default=MISSING)
    _cells_count_at_last_turn: int = 0
    _turns_count: int = 0

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

        cells_count = self._count_of(fig.Figure)
        town_count = self._count_of(fig.Town)
        infantry_count = self._count_of(fig.Infantry)
        motorization_count = self._count_of(fig.Motorization)

        move = (self._try_convert_infantry_to_motorization()
                if (infantry_count + motorization_count) * .3 >= motorization_count
                else MISSING)
        if move is not MISSING:
            return move

        move = self._try_advance_forces()
        if move is not MISSING:
            return move

        move = (self._try_create(fig.Infantry)
                if infantry_count + motorization_count < 5 else
                MISSING)
        if move is not MISSING:
            return move

        figure_to_create = (fig.Town
                            if cells_count >= self._cells_count_at_last_turn * .98 and
                               town_count < cells_count * .2 else
                            ((fig.Tank if random.random() > .85 else fig.Infantry)
                             if cells_count * .2 > (infantry_count + motorization_count + self._count_of(fig.Tank)) else
                             MISSING))

        if figure_to_create is not MISSING:
            move = self._try_create(figure_to_create)
        else:
            print(123)
        if move is not MISSING:
            return move

        move = self._try_pull_forces_to_front()
        if move is not MISSING:
            return move

        self._cells_count_at_last_turn = cells_count
        self._turns_count += 1
        return MISSING

    def _get_cell_for(self, figure: type[fig.Figure]) -> proto.Cell | Status:
        empties = self._board.cells.with_owner(self._player).with_figure(fig.Empty)
        if not empties:
            return MISSING

        front = empties.at_front(self._board)
        back = empties - front
        production = self._board.cells.with_owner(self._player).with_figure(fig.Town)

        match figure:
            # case fig.Infantry:
            #     tanks = self._board.cells.with_owner(self._player).with_figure(fig.Tank)
            #     if not tanks:
            #         return self._get_cell_for_armed_figure(front, production)
            #
            #     tanks_at_front = tanks.at_front(self._board)
            #     if not tanks_at_front:
            #         return self._get_cell_for_armed_figure(front, production)
            #
            #     empties_near_tank: proto.Cells = next(filter(lambda cells: cells,
            #                                                  map(lambda tank:
            #                                                      self._board.get_neighbors(tank, include_cell=False),
            #                                                  tanks_at_front.all())))
            #     if not empties_near_tank:
            #         return self._get_cell_for_armed_figure(front, production)
            #
            #     return random.choice(list(empties_near_tank.all()))

            case fig.Tank:
                front = Cells({cell for cell in front
                               if self._board.get_neighbors(cell, include_cell=False)
                              .with_owner(self._player).with_figure(fig.Infantry)})
                if not front:
                    return MISSING
                return self._get_cell_for_armed_figure(front, production)
            case fig.Infantry | fig.Bunker:
                return self._get_cell_for_armed_figure(front, production)
            case fig.Town:
                candidates = back or empties
                return random.choice(list(candidates.all())[:10])
            case _:
                return random.choice(list(empties.all()))

        assert False

    def _get_cell_for_armed_figure(self, front: proto.Cells, production: proto.Cells) -> proto.Cell | Status:
        if not front:
            return MISSING
        if not production:
            return random.choice(list(front.all()))

        return self._min_sqrt_distance_cell(front, production)

    def _get_target_enemy(self, cell: proto.Cell) -> proto.Cell | Status:
        neighbors = self._board.get_neighbors(cell, include_cell=False)
        if not neighbors:
            return MISSING

        targets = neighbors - neighbors.with_owner(self._player)
        if isinstance(cell.figure, fig.Tank):
            targets = Cells({cell for cell in targets
                             if self._board.get_neighbors(cell, include_cell=False)
                            .with_owner(self._player).with_figure(fig.Infantry)})

        if not targets:
            return MISSING

        empty_targets = targets.with_figure(fig.Empty)
        not_empty_targets = targets - empty_targets
        targets = not_empty_targets or empty_targets

        return random.choice(list(targets.all()))

    def _get_pull_infantry_motorization_cell(self, cell: proto.Cell) -> proto.Cell | Status:
        assert isinstance(cell.figure, fig.Infantry | fig.Motorization)

        all_armed = (self._board.cells
                     .with_owner(self._player)
                     .with_figure(fig.Infantry | fig.Motorization | fig.Tank))
        if not all_armed:
            return MISSING

        front = all_armed.at_front(self._board)
        if not front:
            return MISSING

        neighbors = (self._board
                     .get_neighbors(cell, include_cell=False)
                     .with_owner(self._player)
                     .with_figure(fig.Empty))
        if not neighbors:
            return MISSING

        neighbors = (self._board
                     .get_neighbors(cell, include_cell=True)
                     .with_owner(self._player)
                     .with_figure(fig.Empty))

        target = self._min_sqrt_distance_cell(neighbors, front)
        if target == cell:
            return MISSING

        return target

    def _get_pull_tank_cell(self, cell: proto.Cell) -> proto.Cell | Status:
        assert isinstance(cell.figure, fig.Tank)

        all_armed = (self._board.cells
                     .with_owner(self._player)
                     .with_figure(fig.Infantry | fig.Motorization | fig.Tank))
        if not all_armed:
            return MISSING

        front = all_armed.at_front(self._board)
        front = Cells({cell for cell in front
                       if self._board.get_neighbors(cell, include_cell=False)
                      .with_owner(self._player).with_figure(fig.Infantry)})
        if not front:
            return MISSING

        neighbors = (self._board
                     .get_neighbors(cell, include_cell=False)
                     .with_owner(self._player)
                     .with_figure(fig.Empty))
        if not neighbors:
            return MISSING

        neighbors = (self._board
                     .get_neighbors(cell, include_cell=True)
                     .with_owner(self._player)
                     .with_figure(fig.Empty))

        target = self._min_sqrt_distance_cell(neighbors, front)
        if target == cell:
            return MISSING

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
        for cell in all_armed:
            fn = (self._get_pull_infantry_motorization_cell
                  if not isinstance(cell.figure, fig.Tank)
                  else self._get_pull_tank_cell)
            if (not isinstance(cell.figure, fig.Tank)) and cell not in back:
                continue
            if (target := fn(cell)) is MISSING:
                continue

            move = Relocation(self._board.coordinates_of(cell),
                              self._board.coordinates_of(target))
            if (valid_move := move.validate(self._session)) is not INVALID:
                return valid_move

        return MISSING

    def _try_convert_infantry_to_motorization(self) -> proto.ValidMove | Status:
        infantries = (self._board.cells
                      .with_owner(self._player)
                      .with_figure(fig.Infantry))
        if not infantries:
            return MISSING

        for infantry in infantries:
            move = Conversion(self._board.coordinates_of(infantry),
                              fig.Motorization)
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

        return Creation(figure, self._board.coordinates_of(cell)).validate(self._session) is not INVALID

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

    def _min_sqrt_distance_cell(self, candidates: proto.Cells, targets: proto.Cells) -> proto.Cell:
        return min(candidates, key=lambda front_cell: sum((self._board.coordinates_of(front_cell) -
                                                           self._board.coordinates_of(production_cell)).length ** .25
                                                          for production_cell in targets))
