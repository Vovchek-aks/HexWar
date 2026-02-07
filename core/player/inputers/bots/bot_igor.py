import math
import random
from itertools import islice
from typing import Iterator

from attrs import define, field

from core import protocols as proto
from core.cells import Cells
from core.figures import figure as fig
from core.moves.attack import Attack
from core.moves.capture import Capture
from core.moves.conversion import Conversion
from core.moves.creation import Creation
from core.moves.relocations import Relocation, Assault
from core.moves.valid_move import ValidMove
from core.protocols import Capturable, CanCapture
from mathematics.vector import Vector2Int
from statuses import Status, MISSING, INVALID, IN_PROGRESS, ABORT_NEEDED

_ATTACKING = 0
_BUILDING = 1
_PULLING = 2


@define
class BotIgor(proto.Bot):
    _session: proto.GameSession | Status = field(init=False, default=MISSING)
    _player: proto.Player | Status = field(init=False, default=MISSING)
    _cells_count_at_last_turn: int = 0
    _turns_count: int = 0
    _state: int = _BUILDING
    _moves_to_make: list[proto.ValidMove] = field(factory=list)
    _moves_generator: Iterator[None] | Status = field(init=False, default=MISSING)
    _ran_out_of_moves: bool = field(init=False, default=False)

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
        self._player = session.master.current_player

        if self._moves_generator is not MISSING:
            if next(self._moves_generator, ABORT_NEEDED) is not ABORT_NEEDED:
                return IN_PROGRESS
            self._moves_generator = MISSING

        cells_count = len(session.cells.with_owner(self._player).all())
        if cells_count <= 0:
            return MISSING

        while self._moves_to_make:
            move = self._moves_to_make.pop(0)
            if move.move.validate(session) is not INVALID:
                self._ran_out_of_moves = False
                return move

        if not self._ran_out_of_moves:
            self._moves_generator = self._add_moves(cells_count)
            self._ran_out_of_moves = False
            return IN_PROGRESS

        # print('\n' * 3)
        self._cells_count_at_last_turn = cells_count
        self._turns_count += 1
        self._state = _BUILDING
        self._ran_out_of_moves = False
        return MISSING

    def _add_moves(self, cells_count: int, *, _is_inner=False) -> Iterator[None]:
        cells = self._session.cells
        town_count = self._count_of(fig.Town)
        infantry_count = self._count_of(fig.Infantry)
        motorization_count = self._count_of(fig.Motorization)
        bunkers_count = len((cells.with_owner(self._player) &
                             cells.with_figure(fig.Bunker) &
                             cells.at_front).all())
        empty_front_length = len((cells.with_owner(self._player) &
                                  cells.at_front &
                                  cells.with_figure(fig.Land)).all())
        tanks_count = self._count_of(fig.Tank)

        if self._state == _BUILDING:
            yield from self._try_convert_infantry_to_motorization()
            # print("_try_convert_infantry_to_motorization")
            if self._moves_to_make:
                # print(self._moves_to_make)
                return

            initial_army_size = (len((self._session.cells.with_owner(self._player) &
                                      self._session.cells.at_front).all()) * .3
                                 if town_count > math.ceil(cells_count * 0.05) else 5)

            if infantry_count + motorization_count > 0 and tanks_count < math.ceil(initial_army_size / 10):
                self._try_create(fig.Tank)
                # print("_try_create(fig.Tank)")
                if self._moves_to_make:
                    # print(self._moves_to_make)
                    return

            if infantry_count + motorization_count < initial_army_size:
                self._try_create(fig.Infantry)
                # print("_try_create(fig.Infantry)")
                if self._moves_to_make:
                    # print(self._moves_to_make)
                    return

            if bunkers_count < empty_front_length * .05:
                self._try_create(fig.Bunker)
                # print("_try_create(fig.Bunker)")
                if self._moves_to_make:
                    # print(self._moves_to_make)
                    return

            figure_to_create = (fig.Town
                                if cells_count >= self._cells_count_at_last_turn * .75 and
                                   town_count < cells_count * .15 else
                                (fig.Tank if random.random() > .85 else fig.Infantry))

            if figure_to_create is not MISSING:
                self._try_create(figure_to_create)
                # print(f"_try_create({figure_to_create})")
                if self._moves_to_make:
                    # print(self._moves_to_make)
                    return

            self._state = _ATTACKING

        if self._state == _ATTACKING:
            yield from self._try_capture()
            # print("_try_capture")
            if self._moves_to_make:
                # print(self._moves_to_make)
                return
            yield from self._try_breakthrough_with_tanks()
            # print("_try_breakthrough_with_tanks")
            if self._moves_to_make:
                # print(self._moves_to_make)
                return
            yield from self._try_advance_forces()
            # print("_try_advance_forces")
            if self._moves_to_make:
                # print(self._moves_to_make)
                return
            yield from self._try_attack_with_tanks()
            # print("_try_attack_with_tanks")
            if self._moves_to_make:
                # print(self._moves_to_make)
                return

            self._state = _PULLING

        if self._state == _PULLING:
            yield from self._try_pull_forces_to_front()
            # print(f"_try_pull_forces_to_front {_is_inner}")
            if self._moves_to_make:
                # print(self._moves_to_make)
                return

            if not _is_inner:
                self._state = _BUILDING
                yield from self._add_moves(cells_count, _is_inner=True)
            else:
                self._ran_out_of_moves = True

    def _get_cell_for(self, figure: type[fig.Figure]) -> proto.Cell | Status:
        cells = self._session.cells
        own_cells = cells.with_owner(self._player)
        empties = own_cells & cells.with_figure(fig.Land)
        if not empties:
            return MISSING

        front = empties & cells.at_front
        back = empties - front
        production = own_cells & cells.with_figure(fig.Town)

        match figure:
            case fig.Tank:
                front = Cells({cell for cell in front
                               if self._board.get_neighbors(cell, include_cell=False).with_flag(proto.OnLand)
                              .with_owner(self._player).with_figure(fig.Infantry)})
                if not front:
                    return MISSING
                return self._get_cell_for_armed_figure(front, production)
            case fig.Infantry | fig.Bunker:
                return self._get_cell_for_armed_figure(front, production)
            case fig.Town:
                candidates = back or empties
                return random.choice(list(candidates.all()))
            case _:
                return random.choice(list(empties.all()))

        assert False

    def _get_cell_for_armed_figure(self,
                                   front: proto.Cells,
                                   production: proto.Cells) -> proto.Cell | Status:
        if not front:
            return MISSING
        if not production:
            return random.choice(list(front.all()))

        unsafe_front = self._get_unsafe_front(front)
        if unsafe_front:
            front = unsafe_front

        return self._min_sqrt_distance_cell(front, production)

    def _get_unsafe_front(self, front: Cells) -> Cells:
        unsafe = set[proto.Cell]()
        for cell in front:
            neighbors = self._session.board.get_neighbors(cell).with_flag(proto.OnLand)
            enemies = neighbors - neighbors.with_owner(self._player)
            armed_enemies = enemies - enemies.with_figure(fig.Land)
            if armed_enemies:
                unsafe.add(cell)
        return Cells(unsafe)

    def _get_target_enemy(self, cell: proto.Cell) -> proto.Cell | Status:
        neighbors = self._board.get_neighbors(cell, include_cell=False).with_flag(proto.OnLand)
        if not neighbors:
            return MISSING

        targets = neighbors - neighbors.with_owner(self._player)
        if isinstance(cell.figure, fig.Tank):
            targets = Cells({cell for cell in targets
                             if self._board.get_neighbors(cell, include_cell=False).with_flag(proto.OnLand)
                            .with_owner(self._player).with_figure(fig.Infantry | fig.Motorization)})

        if not targets:
            return MISSING

        empty_targets = targets.with_figure(fig.Land)
        not_empty_targets = targets - empty_targets
        targets = not_empty_targets or empty_targets

        return random.choice(list(targets.all()))

    def _get_pull_infantry_motorization_cell(self, cell: proto.Cell) -> proto.Cell | Status:
        assert isinstance(cell.figure, fig.Infantry | fig.Motorization)

        cells = self._session.cells
        all_armed = (cells.with_owner(self._player) &
                     cells.with_figure(fig.Infantry | fig.Motorization | fig.Tank))
        if not all_armed:
            return MISSING

        front = all_armed & cells.at_front
        if not front:
            return MISSING

        neighbors = (self._board
                     .get_neighbors(cell, include_cell=False)
                     .with_flag(proto.OnLand)
                     .with_owner(self._player)
                     .with_figure(fig.Land))
        if not neighbors:
            return MISSING

        neighbors += Cells({cell})

        target = self._min_sqrt_distance_cell(neighbors, front)
        if target == cell:
            return MISSING

        return target

    def _get_pull_tank_cell(self, cell: proto.Cell) -> proto.Cell | Status:
        if not isinstance(cell.figure, fig.Tank):
            assert False

        cells = self._session.cells
        all_armed = (cells.with_owner(self._player) &
                     cells.with_figure(fig.Infantry | fig.Motorization | fig.Tank))
        if not all_armed:
            return MISSING

        front = all_armed & self._session.cells.at_front

        front = Cells({cell for cell in front
                       if self._board.get_neighbors(cell, include_cell=False).with_flag(proto.OnLand)
                      .with_owner(self._player).with_figure(fig.Infantry | fig.Motorization)})
        if not front:
            return MISSING

        neighbors = (self._board
                     .get_neighbors(cell, include_cell=False)
                     .with_flag(proto.OnLand)
                     .with_owner(self._player)
                     .with_figure(fig.Land))
        if not neighbors:
            return MISSING

        neighbors += Cells({cell})

        target = self._min_sqrt_distance_cell(neighbors, front)
        if target == cell:
            return MISSING

        return target

    def _try_pull_forces_to_front(self) -> Iterator[None]:
        cells = self._session.cells
        all_armed = (cells.with_owner(self._player) &
                     cells.with_figure(fig.Infantry | fig.Motorization | fig.Tank))
        if not all_armed:
            return

        front = all_armed & self._session.cells.at_front
        if not front:
            return
        yield

        back = all_armed - front
        for cell in all_armed:
            fn = (self._get_pull_infantry_motorization_cell
                  if (is_infmoto := isinstance(cell.figure, fig.Motorization | fig.Infantry))
                  else self._get_pull_tank_cell)
            if is_infmoto and cell not in back:
                yield
                continue
            if (target := fn(cell)) is MISSING:
                yield
                continue

            move = Relocation(self._board.coordinates_of(cell),
                              self._board.coordinates_of(target))
            if (valid_move := move.validate(self._session)) is not INVALID:
                self._moves_to_make.append(valid_move)
            yield

    def _try_convert_infantry_to_motorization(self) -> Iterator[None]:
        infantries = (self._session.cells.with_owner(self._player) &
                      self._session.cells.with_figure(fig.Infantry))
        if not infantries:
            return
        yield

        infantry_count = len(infantries.all())
        motorization_count = self._count_of(fig.Motorization)
        to_convert = max(0, math.floor((infantry_count + motorization_count) * .5 - motorization_count))
        yield

        for infantry in islice(infantries.all(), 0, to_convert):
            move = Conversion(self._board.coordinates_of(infantry),
                              fig.Motorization)
            if (valid_move := move.validate(self._session)) is not INVALID:
                self._moves_to_make.append(valid_move)
            yield

    def _try_advance_forces(self) -> Iterator[None]:
        cells = self._session.cells
        all_armed = (cells.with_owner(self._player) &
                     cells.with_figure(fig.Infantry | fig.Motorization | fig.Tank))
        if not all_armed:
            return
        yield

        armed_front = all_armed & cells.at_front
        if not armed_front:
            return
        yield

        for cell in armed_front:
            if (target := self._get_target_enemy(cell)) is MISSING:
                yield
                continue

            move = Assault(self._board.coordinates_of(cell),
                           self._board.coordinates_of(target))
            if (valid_move := move.validate(self._session)) is not INVALID:
                self._moves_to_make.append(valid_move)
            yield

    def _try_breakthrough_with_tanks(self) -> Iterator[None]:
        cells = self._session.cells
        tanks = (cells.with_owner(self._player) &
                 cells.with_figure(fig.Tank) &
                 cells.at_front)
        if not tanks:
            return
        yield

        for cell in tanks:
            if (target := self._get_target_enemy(cell)) is MISSING:
                yield
                continue

            supports = (self._session.board
                        .get_neighbors(cell)
                        .with_owner(self._player)
                        .with_figure(fig.Motorization | fig.Infantry))
            if not supports:
                continue

            support = min((sup.figure for sup in supports.all()),
                          key=lambda figure: self._session.figures_budget.of(figure) /
                                             figure.get_cost_of(Relocation(Vector2Int.zero(), Vector2Int.zero())))
            if not self._session.figures_budget.can_spend(support, support.get_cost_of(Relocation(Vector2Int.zero(),
                                                                                                  Vector2Int.zero()))):
                continue

            support_coord = self._session.figures.locate(support)

            assault = Assault(self._board.coordinates_of(cell),
                              self._board.coordinates_of(target))
            relocation = Relocation(support_coord,
                                    self._board.coordinates_of(cell))
            if (valid_move := assault.validate(self._session)) is not INVALID:
                self._moves_to_make.append(valid_move)
                self._moves_to_make.append(ValidMove(relocation))
            yield

    def _try_attack_with_tanks(self) -> Iterator[None]:
        tanks = (self._session.cells.with_owner(self._player) &
                 self._session.cells.with_figure(fig.Tank))
        if not tanks:
            return
        yield

        for tank in tanks.at_front(self._board):
            neighbors = self._board.get_neighbors(tank, include_cell=False).with_flag(proto.OnLand)
            neighbors -= neighbors.with_owner(self._player)
            neighbors -= neighbors.with_figure(fig.Land)
            if not neighbors:
                yield
                continue

            target: proto.Cell = random.choice(list(neighbors.all()))
            move = Attack(self._board.coordinates_of(tank),
                          self._board.coordinates_of(target))
            if (valid_move := move.validate(self._session)) is not INVALID:
                self._moves_to_make.append(valid_move)
            yield

    def _try_capture(self) -> Iterator[None]:
        infantries = self._session.cells.with_owner(self._player).with_flag(CanCapture)
        if not infantries:
            return
        yield

        for infantry in infantries & self._session.cells.at_front:
            neighbors = (self._board.get_neighbors(infantry, include_cell=False)
                         .with_flag(Capturable)
                         .with_flag(proto.OnLand))
            neighbors -= neighbors.with_owner(self._player)
            neighbors -= neighbors.with_figure(fig.Land)
            if not neighbors:
                yield
                continue

            target: proto.Cell = random.choice(list(neighbors.all()))
            move = Capture(self._board.coordinates_of(infantry),
                           self._board.coordinates_of(target))
            if (valid_move := move.validate(self._session)) is not INVALID:
                self._moves_to_make.append(valid_move)
            yield

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

    def _try_create(self, figure: type[fig.Figure]) -> None:
        if (cell := self._get_cell_for(figure)) is MISSING:
            return

        if not self._can_create(figure, cell):
            return

        valid_move = self._create(figure, cell)
        self._moves_to_make.append(valid_move)

    def _count_of(self, figure: type[fig.Figure]) -> int:
        cells = self._session.cells
        res = len((cells.with_owner(self._player) &
                   cells.with_figure(figure)).all())
        return res

    def _min_sqrt_distance_cell(self, candidates: proto.Cells, targets: proto.Cells) -> proto.Cell:
        # return list(candidates.all())[0]
        coord_of = self._board.coordinates_of
        return min(candidates, key=lambda front_cell: sum((coord_of(front_cell) -
                                                           coord_of(production_cell)).length ** .25
                                                          for production_cell in targets))
