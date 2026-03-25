import math
import random
from itertools import islice
from typing import Iterator
from time import time

from attrs import define, field

from core import protocols as proto
from core.cells import Cells
from core.distant_neighbors_getter import DistantNeighborsGetter
from core.figures import figure as fig
from core.figures.resources_flow_flags import getting_resources_flow_process
from core.moves.attack import Attack
from core.moves.capture import Capture
from core.moves.conversion import Conversion
from core.moves.creation import Creation
from core.moves.oreshnik_launch import OreshnikLaunch
from core.moves.pulling import PullingInitiation
from core.moves.relocations import Relocation, Assault
from core.moves.valid_move import ValidMove
from core.protocols import Capturable, CanCapture
from core.resources import Dollars, LightIndustryProducts, HeavyIndustryProducts, Resource, ResourcesGroup
from mathematics.greedy_path_searcher import GreedyPathSearcher
from mathematics.hex_geometry import get_distance
from mathematics.vector import Vector2Int
from statuses import Status, MISSING, INVALID, IN_PROGRESS, ABORT_NEEDED

_ATTACKING = 0
_BUILDING = 1
_PULLING = 2
_CATASTROPHY_PREVENTION = 3
_INITIAL_STATE = _CATASTROPHY_PREVENTION

_TARGET_FLOW_PER_CELL_OF = ResourcesGroup.make(
    Dollars(5_000),
    LightIndustryProducts(5),
    HeavyIndustryProducts(5),
)

_PRODUCER_OF: dict[type[Resource], type[fig.Figure]] = {
    Dollars: fig.Town,
    LightIndustryProducts: fig.LightFactory,
    HeavyIndustryProducts: fig.HeavyFactory,
}

_MAX_ARMY = 150.

PRODUCTION = fig.Town | fig.Capital | fig.LightFactory | fig.HeavyFactory


@define
class BotIgor(proto.Bot):
    _session: proto.GameSession | Status = field(init=False, default=MISSING)
    _player: proto.Player | Status = field(init=False, default=MISSING)
    _cells_count_at_last_turn: int = 0
    _turns_count: int = 0
    _state: int = _INITIAL_STATE
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

        random.seed(time())

        if self._moves_generator is not MISSING:
            if next(self._moves_generator, ABORT_NEEDED) is not ABORT_NEEDED:
                return IN_PROGRESS
            self._moves_generator = MISSING

        cells_count = len(session.cells.with_owner(self._player))
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
        self._state = _INITIAL_STATE
        self._ran_out_of_moves = False
        return MISSING

    def _add_moves(self, cells_count: int, *, _is_inner=False) -> Iterator[None]:
        cells = self._session.cells
        town_count = self._count_of(fig.Town)
        infantry_count = self._count_of(fig.Infantry)
        artillery_count = self._count_of(fig.Artillery)
        motorization_count = self._count_of(fig.Motorization)
        bunkers_count = len((cells.with_owner(self._player) &
                             cells.with_figure(fig.Bunker) &
                             cells.at_front).as_set())
        empty_front_length = len((cells.with_owner(self._player) &
                                  cells.at_front &
                                  cells.with_figure(fig.Land)).as_set())
        tanks_count = self._count_of(fig.Tank)
        silos_count = self._count_of(fig.MissileSilo)

        if self._state == _CATASTROPHY_PREVENTION:
            for figure in fig.Capital, fig.Town, fig.LightFactory:
                if self._count_of(figure) == 0:
                    self._try_create(figure)
                    # print(f"_try_create({figure})")
                    if self._moves_to_make:
                        # print(self._moves_to_make)
                        return

            if self._count_of(fig.Capital) < cells_count / 200:
                self._try_create(fig.Capital)
                # print("_try_create(fig.Capital)")
                if self._moves_to_make:
                    # print(self._moves_to_make)
                    return

            initial_army_size = min(_MAX_ARMY, .1 * len(cells.with_owner(self._player) & cells.at_front))

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

            self._state = _BUILDING

        if self._state == _BUILDING:
            has_developed = town_count > cells_count * .01
            is_rich = self._player.resources.get(Dollars).amount / 1_000_000 > town_count

            bunker_ratio = .1 if has_developed and not is_rich else 0.75
            if bunkers_count < empty_front_length * bunker_ratio:
                self._try_create(fig.Bunker)
                # print("_try_create(fig.Bunker)")
                if self._moves_to_make:
                    # print(self._moves_to_make)
                    return

            if has_developed:
                for silo in cells.with_owner(self._player) & cells.with_figure(fig.MissileSilo):
                    yield from self._try_launch_oreshnik(self._board.coordinates_of(silo))
                    # print("_try_launch_oreshnik")
                    if self._moves_to_make:
                        # print(self._moves_to_make)
                        return

            target_silos_count = max(1, town_count // 20)
            if silos_count < target_silos_count:
                self._try_create(fig.MissileSilo)
                # print("_try_create(fig.MissileSilo)")
                if self._moves_to_make:
                    # print(self._moves_to_make)
                    return

            if has_developed:
                yield from self._try_convert_infantry_to_motorization()
                # print("_try_convert_infantry_to_motorization")
                if self._moves_to_make:
                    # print(self._moves_to_make)
                    return

            yield from self._try_connect_pullerless_artillery()
            # print("_try_connect_pullerless_artillery")
            if self._moves_to_make:
                # print(self._moves_to_make)
                return

            if has_developed:
                yield from self._try_spawn_and_connect_artillery(math.ceil((infantry_count + motorization_count) * .3) -
                                                                 artillery_count)
                # print("_try_spawn_and_connect_artillery")
                if self._moves_to_make:
                    # print(self._moves_to_make)
                    return

            yield from self._try_align_resources_flow(cells_count)
            # print("_try_align_resources_flow")
            if self._moves_to_make:
                # print(self._moves_to_make)
                return

            if infantry_count + tanks_count + artillery_count + motorization_count < _MAX_ARMY:
                figure_to_create = fig.Tank if random.random() > .85 else fig.Infantry
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

            yield from self._try_attack_with_artillery()
            # print("_try_attack_with_artillery")
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
        production = own_cells & cells.with_figure(PRODUCTION)
        capitals = cells.with_figure(fig.Capital) & cells.with_owner(self._player)

        match figure:
            case fig.Tank:
                front = Cells({cell for cell in front
                               if self._board.get_neighbors(cell, include_cell=False).with_flag(proto.OnLand)
                              .with_owner(self._player).with_figure(fig.Infantry)})
                if not front:
                    return MISSING
                return self._get_cell_for_armed_figure(front, production)

            case fig.Infantry:
                return self._get_cell_for_armed_figure(front, production)

            case fig.Bunker:
                return self._get_cell_for_bunker(front, production)

            case fig.Capital:
                candidates = back or empties
                max_points = -float("inf")
                target: proto.Cell | Status = MISSING
                for candidate in candidates:
                    min_distance_to_other_capital = min(get_distance(self._board.coordinates_of(candidate),
                                                                     self._board.coordinates_of(capital))
                                                        for capital in capitals) if capitals else float('inf')
                    if min_distance_to_other_capital < 10:
                        continue

                    neighbors = self._board.get_neighbors(candidate).with_owner(self._player)
                    points = len(neighbors.with_figure(fig.Land))
                    points += len(neighbors.with_flag(proto.ResourcesAdder)) * 100

                    if points > max_points:
                        max_points = points
                        target = candidate

                return target

            case fig.Town | fig.LightFactory | fig.HeavyFactory:
                for capital in capitals:
                    neighbors = self._board.get_neighbors(capital).with_owner(self._player).with_figure(fig.Land)
                    if neighbors:
                        return random.choice(neighbors.as_list())

                candidates = back or empties
                return random.choice(candidates.as_list())

            case fig.MissileSilo:
                candidates = back or empties
                return random.choice(candidates.as_list())

            case _:
                return random.choice(empties.as_list())

        assert False

    def _get_cell_for_bunker(self,
                             front: proto.Cells,
                             production: proto.Cells) -> proto.Cell | Status:
        candidates = set[proto.Cell]()
        for candidate in front:
            nearby_bunkers = (self._session.board
                              .get_neighbors(candidate)
                              .with_owner(self._player)
                              .with_figure(fig.Bunker))
            if not nearby_bunkers:
                candidates.add(candidate)

        cell = self._get_cell_for_armed_figure(Cells(candidates), production)
        if cell is not MISSING:
            return cell
        return self._get_cell_for_armed_figure(front, production)

    def _get_cell_for_armed_figure(self,
                                   front: proto.Cells,
                                   production: proto.Cells) -> proto.Cell | Status:
        if not front:
            return MISSING
        if not production:
            return random.choice(list(front.as_set()))

        unsafe_front = self._get_unsafe_front(front)
        if unsafe_front:
            front = unsafe_front

        return self._min_sqrt_distance_cell(front, production)

    def _get_unsafe_front(self, front: Cells) -> Cells:
        unsafe = set[proto.Cell]()
        for cell in front:
            neighbors = self._session.board.get_neighbors(cell).with_flag(proto.OnLand)
            enemies = neighbors - neighbors.with_owner(self._player)
            armed_enemies = enemies - enemies.with_figure(fig.Land | fig.Bunker)
            if armed_enemies:
                unsafe.add(cell)
        return Cells(unsafe)

    def _get_front_near_armed(self, front: Cells) -> Cells:
        near_armed = set[proto.Cell]()
        for cell in front:
            armed = (self._session.board
                     .get_neighbors(cell)
                     .with_owner(self._player)
                     .with_figure(fig.Infantry | fig.Motorization | fig.Tank | fig.Artillery | fig.Bunker))
            if armed:
                near_armed.add(cell)
        return Cells(near_armed)

    def _try_align_resources_flow(self, cells_count: int) -> Iterator[None]:
        figures_to_build = list[type[fig.Figure]]()
        yield from self._fill_figures_to_build(figures_to_build, cells_count, max_iterations=100)
        for figure in figures_to_build:
            yield
            self._try_create(figure)

    def _fill_figures_to_build(self,
                               figures_to_build: list[type[fig.Figure]],
                               cells_count: int,
                               *,
                               max_iterations: int | float = float('inf')) -> Iterator[None]:
        resources = list(map(type[Resource], _TARGET_FLOW_PER_CELL_OF))

        target_flow = _TARGET_FLOW_PER_CELL_OF * cells_count
        flow = ResourcesGroup()
        for resource in resources:
            for result in self._getting_flow_process(resource):
                yield
                if result is not MISSING:
                    flow += ResourcesGroup.make(resource(result))

        iterations = 0
        while (pair := self._get_resource_with_max_unfilled_demand(resources, flow, target_flow))[-1] > 1:
            iterations += 1
            if iterations > max_iterations:
                return
            yield

            resource, _ = pair
            figure = _PRODUCER_OF[resource]
            figures_to_build.append(figure)

            if (adder := figure.FLAGS.get(proto.ResourcesAdder)) is not MISSING:
                flow += adder.base_resources
            if (taker := figure.FLAGS.get(proto.ResourcesTaker)) is not MISSING:
                flow -= taker.resources_to_take

    def _get_resource_with_max_unfilled_demand(self,
                                               resources: list[type[Resource]],
                                               flow: ResourcesGroup,
                                               target_flow: ResourcesGroup) -> tuple[type[Resource], float]:
        return max(map(lambda resource: (resource, self._get_lack_for(resource, flow, target_flow)), resources),
                   key=lambda pair: pair[-1])

    @staticmethod
    def _get_lack_for(resource: type[Resource], flow: ResourcesGroup, target_flow: ResourcesGroup) -> float:
        current_flow = flow.get(resource).amount
        lack = target_flow.get(resource).amount / max(1, abs(current_flow))
        return lack if current_flow > 0 else lack ** 2

    def _getting_flow_process(self, resource: type[Resource]) -> Iterator[Status | int]:
        return getting_resources_flow_process(self._player, resource, self._session)

    def _try_launch_oreshnik(self, silo_coord: Vector2Int) -> Iterator[None]:
        silo = self._board[silo_coord]
        assert isinstance(silo.figure, fig.MissileSilo)

        if not self._player.resources.can_take(silo.figure.FLAGS.get(proto.CanLaunchOreshnik).cost):
            return

        if not self._session.figures_budget.can_spend(silo.figure,
                                                      silo.figure.get_cost_of(OreshnikLaunch(Vector2Int.zero(),
                                                                                             Vector2Int.zero()))):
            return

        cells = self._session.cells

        targets = list[tuple[Cells, Cells]]()
        for player in self._session.master.players:
            yield
            if player == self._player:
                continue

            to_player_front = Cells()
            for front in cells.at_front & cells.with_owner(player):
                to_player_front += self._board.get_neighbors(front)
            if not cells.with_owner(self._player) & to_player_front:
                continue

            silos = cells.with_owner(player) & cells.with_figure(fig.MissileSilo)

            targets.append((silos,
                            cells.with_owner(player) & cells.with_figure(PRODUCTION)))

        target = max(targets, key=lambda t: (len(t[1].as_set()), -len(t[0].as_set())))

        for cell in target[0]:
            yield
            move = OreshnikLaunch(silo_coord, self._board.coordinates_of(cell))
            if (valid_move := move.validate(self._session)) is INVALID:
                continue

            self._moves_to_make.append(valid_move)
            return

        valid_moves = list[OreshnikLaunch]()
        for cell in target[1]:
            yield
            move = OreshnikLaunch(silo_coord, self._board.coordinates_of(cell))
            if (move.get_target_cells(self._session) &
                    cells.with_owner(self._player) -
                    cells.with_figure(fig.Land | fig.Water)):
                continue

            if move.validate(self._session) is not INVALID:
                valid_moves.append(move)

        if not valid_moves:
            return

        most_profitable = max(valid_moves, key=lambda move: len((move.get_target_cells(self._session) -
                                                                 cells.with_figure(fig.Land | fig.Water)).as_set()))
        self._moves_to_make.append(ValidMove(most_profitable))

    def _try_spawn_and_connect_artillery(self, amount: int) -> Iterator[None]:
        if amount <= 0:
            return

        cells = self._session.cells
        infantries = (cells.with_owner(self._player) &
                      cells.with_figure(fig.Infantry))
        if not infantries:
            return
        yield

        not_puller = {infantry for infantry in infantries
                      if not self._session.pulling_connections.is_puller(infantry.figure)}
        if not not_puller:
            return
        yield

        added = 0
        for cell in not_puller:
            places = self._board.get_neighbors(cell).with_owner(self._player).with_figure(fig.Land)
            if not places:
                yield
                continue

            place = random.choice(list(places.as_set()))
            make = Creation(fig.Artillery, self._board.coordinates_of(place))
            connect = PullingInitiation(self._board.coordinates_of(place), self._board.coordinates_of(cell))
            if (valid_move := make.validate(self._session)) is not INVALID:
                self._moves_to_make.append(valid_move)
                self._moves_to_make.append(ValidMove(connect))
                added += 1
                if added >= amount:
                    return
            yield

    def _try_connect_pullerless_artillery(self) -> Iterator[None]:
        cells = self._session.cells
        artilleries = (cells.with_owner(self._player) &
                       cells.with_figure(fig.Artillery))
        if not artilleries:
            return
        yield

        not_pullable = {artillery for artillery in artilleries
                        if not self._session.pulling_connections.is_pullable(artillery.figure)}
        if not not_pullable:
            return
        yield

        for cell in not_pullable:
            places = self._board.get_neighbors(cell).with_owner(self._player).with_figure(fig.Land)
            if not places:
                yield
                continue

            place = random.choice(list(places.as_set()))
            make = Creation(fig.Infantry, self._board.coordinates_of(place))
            connect = PullingInitiation(self._board.coordinates_of(cell), self._board.coordinates_of(place))
            if (valid_move := make.validate(self._session)) is not INVALID:
                self._moves_to_make.append(valid_move)
                self._moves_to_make.append(ValidMove(connect))
            yield

    def _get_target_enemy(self, cell: proto.Cell, *, save_tanks: bool = True) -> proto.Cell | Status:
        neighbors = self._board.get_neighbors(cell, include_cell=False).with_flag(proto.OnLand)
        if not neighbors:
            return MISSING

        targets = neighbors - neighbors.with_owner(self._player)
        if isinstance(cell.figure, fig.Tank) and save_tanks:
            targets = Cells({cell for cell in targets
                             if self._board.get_neighbors(cell, include_cell=False).with_flag(proto.OnLand)
                            .with_owner(self._player).with_figure(fig.Infantry | fig.Motorization)})

        if not targets:
            return MISSING

        empty_targets = targets.with_figure(fig.Land)
        not_empty_targets = targets - empty_targets
        targets = not_empty_targets or empty_targets

        return random.choice(list(targets.as_set()))

    def _try_pull_forces_to_front(self) -> Iterator[None]:
        cells = self._session.cells
        all_armed = (cells.with_owner(self._player) &
                     cells.with_figure(fig.Infantry | fig.Motorization | fig.Tank))
        if not all_armed:
            return

        tanks = all_armed.with_figure(fig.Tank)
        not_tanks = all_armed - tanks

        for cell in not_tanks:
            yield
            target = self._get_pull_infantry_motorization_cell(cell)
            if target is MISSING:
                continue

            self._add_distant_relocation_moves(cell, target)
            if self._moves_to_make:
                return

        for cell in tanks:
            yield
            target = self._get_pull_tank_cell(cell)
            if target is MISSING:
                continue

            self._add_distant_relocation_moves(cell, target)
            if self._moves_to_make:
                return

    # def _get_pull_cell_and_pull(self,
    #                             to_pull: Cells,
    #                             pull_cell_getter: Callable[[proto.Cell], proto.Cell]) -> Iterator[None]:
    #     for cell in to_pull:
    #         yield
    #         target = pull_cell_getter(cell)
    #         if target is MISSING:
    #             continue
    #
    #         self._add_distant_relocation_moves(cell, target)
    #         if self._moves_to_make:
    #             return

    def _add_distant_relocation_moves(self, cell: proto.Cell, target: proto.Cell) -> None:
        cells = self._session.cells
        path = (GreedyPathSearcher(self._board,
                                   cells.with_figure(fig.Land) &
                                   cells.with_owner(self._player) +
                                   Cells({cell, target}),
                                   target)
                .search_from(cell))
        if len(path) < 2:
            return

        if Relocation(path[0], path[1]).validate(self._session) is INVALID:
            return

        for previous, new in zip(path[:-1], path[1:]):
            self._moves_to_make.append(ValidMove(Relocation(previous, new)))

    def _get_pull_infantry_motorization_cell(self, cell: proto.Cell) -> proto.Cell | Status:
        assert isinstance(cell.figure, fig.Infantry | fig.Motorization)

        cells = self._session.cells
        front = cells.at_front & cells.with_owner(self._player)

        if cell in front:
            return MISSING

        empty_front = front & cells.with_figure(fig.Land)
        if not empty_front:
            return MISSING

        target_front = min(empty_front.as_set(),
                           key=lambda front_cell: get_distance(self._board.coordinates_of(cell),
                                                               self._board.coordinates_of(front_cell)))

        return target_front

    def _get_pull_tank_cell(self, cell: proto.Cell) -> proto.Cell | Status:
        if not isinstance(cell.figure, fig.Tank):
            assert False

        cells = self._session.cells
        front = cells.at_front & cells.with_owner(self._player)
        if not front:
            return MISSING

        is_safe = bool(self._session.board
                       .get_neighbors(cell)
                       .with_owner(self._player)
                       .with_figure(fig.Infantry | fig.Motorization))
        if cell in front and is_safe:
            return MISSING

        front = Cells({cell for cell in front & cells.with_figure(fig.Land)
                       if self._board.get_neighbors(cell, include_cell=False).with_flag(proto.OnLand)
                      .with_owner(self._player).with_figure(fig.Infantry | fig.Motorization)})
        if not front:
            return MISSING

        target_front = min(front.as_set(),
                           key=lambda front_cell: get_distance(self._board.coordinates_of(cell),
                                                               self._board.coordinates_of(front_cell)))
        return target_front

    def _try_convert_infantry_to_motorization(self) -> Iterator[None]:
        cells = self._session.cells
        infantries = cells.with_owner(self._player) & cells.with_figure(fig.Infantry)
        if not infantries:
            return
        yield

        infantry_count = len(infantries.as_set())
        motorization_count = self._count_of(fig.Motorization)
        to_convert = max(0, math.floor((infantry_count + motorization_count) * .5 - motorization_count))
        yield

        for infantry in islice(infantries.as_set(), 0, to_convert):
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
            if (target := self._get_target_enemy(cell, save_tanks=False)) is MISSING:
                yield
                continue

            supports = (self._session.board
                        .get_neighbors(cell)
                        .with_owner(self._player)
                        .with_figure(fig.Motorization | fig.Infantry))
            if not supports:
                continue

            support = min((sup.figure for sup in supports.as_set()),
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

            target: proto.Cell = random.choice(list(neighbors.as_set()))
            move = Attack(self._board.coordinates_of(tank),
                          self._board.coordinates_of(target))
            if (valid_move := move.validate(self._session)) is not INVALID:
                self._moves_to_make.append(valid_move)
            yield

    def _try_attack_with_artillery(self) -> Iterator[None]:
        artilleries = (self._session.cells.with_owner(self._player) &
                       self._session.cells.with_figure(fig.Artillery))
        if not artilleries:
            return
        yield

        for artillery in artilleries:
            neighbors = (DistantNeighborsGetter(artillery, self._board)
                         .get_all_not_farther_than(fig.Artillery.FLAGS.get(proto.CanAttack).max_distance,
                                                   include_cell=False)
                         .with_flag(proto.OnLand))
            neighbors -= neighbors.with_owner(self._player)
            neighbors -= neighbors.with_figure(fig.Land)
            if not neighbors:
                yield
                continue

            targets = neighbors.with_figure(fig.Artillery)
            if not targets:
                targets = neighbors.with_figure(fig.Tank | fig.Bunker)
            if not targets:
                targets = neighbors

            target = max(targets.as_set(), key=lambda cell: cell.hardness(self._board))
            move = Attack(self._board.coordinates_of(artillery),
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

            target: proto.Cell = random.choice(list(neighbors.as_set()))
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
                   cells.with_figure(figure)).as_set())
        return res

    def _min_sqrt_distance_cell(self, candidates: proto.Cells, targets: proto.Cells) -> proto.Cell:
        coord_of = self._board.coordinates_of
        return min(candidates, key=lambda front_cell: sum((coord_of(front_cell) -
                                                           coord_of(production_cell)).length ** .25
                                                          for production_cell in targets))
