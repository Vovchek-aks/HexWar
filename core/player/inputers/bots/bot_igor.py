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
from core.moves.comnination import Combination
from core.moves.conversion import Conversion
from core.moves.creation import Creation
from core.moves.oreshnik_launch import OreshnikLaunch
from core.moves.pulling import PullingInitiation
from core.moves.relocations import Relocation, Assault
from core.moves.valid_move import ValidMove
from core.protocols import Capturable, CanCapture
from core.resources import Dollars, LightIndustryProducts, HeavyIndustryProducts, Resource, ResourcesGroup
from mathematics.a_star_path_searcher import AStarPathSearcher as PathSearcher
from mathematics.hex_geometry import get_distance
from mathematics.vector import Vector2Int
from statuses import Status, MISSING, INVALID, IN_PROGRESS, ABORT_NEEDED

_ATTACKING = 0
_BUILDING = 1
_PULLING = 2
_CATASTROPHY_PREVENTION = 3
_INITIAL_STATE = _CATASTROPHY_PREVENTION

# https://www.desmos.com/calculator/zkc3ewscyj
_TARGET_RESERVE_RATIO_OF = ResourcesGroup.make(
    Dollars(1_340_000),
    LightIndustryProducts(8_000),
    HeavyIndustryProducts(7_500),
)

_PRODUCER_OF: dict[type[Resource], type[fig.Figure]] = {
    Dollars: fig.Town,
    LightIndustryProducts: fig.LightFactory,
    HeavyIndustryProducts: fig.HeavyFactory,
}

_NOT_PRIVATE_VERSION_OF: dict[type[fig.Figure], type[fig.Figure]] = {
    fig.Settlement: fig.Town,
    fig.PrivateLightFactory: fig.LightFactory,
    fig.PrivateHeavyFactory: fig.HeavyFactory,
}

_NOT_TO_CAPTURE = {
    fig.Abandonment
}

_ARTILLERY_PRIORITY_LIST = [
    fig.Tank,
    fig.Bunker,
    fig.Howitzer,
    fig.Artillery,
    fig.Figure,
]

_MAX_ARMY = 150.

_CAPITALS_RATIO = 2

_HOWITZERS_TO_TANKS_RATIO = .3

_CATASTROPHY_ABANDONMENTS_COUNT = 3

PRODUCTION = (fig.Town | fig.LightFactory | fig.HeavyFactory | fig.Settlement | fig.PrivateLightFactory |
              fig.PrivateHeavyFactory)
CRITICAL = PRODUCTION | fig.Capital


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
        lf_count = self._count_of(fig.LightFactory)
        hf_count = self._count_of(fig.HeavyFactory)
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
        howitzers_count = self._count_of(fig.Howitzer)
        silos_count = self._count_of(fig.MissileSilo)

        if self._state == _CATASTROPHY_PREVENTION:
            for figure in fig.TierOneCapital, fig.Town, fig.LightFactory, fig.HeavyFactory:
                if self._count_of(figure) == 0:
                    self._try_create(figure)
                    # print(f"_try_create({figure})")
                    if self._moves_to_make:
                        # print(self._moves_to_make)
                        return

            if lf_count == 0:
                self._ran_out_of_moves = True
                return

            if artillery_count == 0:
                yield from self._try_spawn_artillery(1)
                # print("_try_spawn_and_connect_artillery")
                if self._moves_to_make:
                    # print(self._moves_to_make)
                    return

            is_any_to_develop = any(self._board
                                    .get_neighbors(cell)
                                    .with_owner(self._player)
                                    .with_figure(fig.Land)
                                    for cell in (cells.with_figure(fig.Capital) &
                                                 cells.with_owner(self._player)))

            if (not is_any_to_develop) and self._count_of(fig.Capital) < math.ceil(_CAPITALS_RATIO *
                                                                                   cells_count ** .25):
                self._try_create(fig.TierOneCapital)
                # print("_try_create(fig.Capital)")
                if self._moves_to_make:
                    # print(self._moves_to_make)
                    return

            initial_army_size = min(_MAX_ARMY, .2 * len(cells.with_owner(self._player) & cells.at_front))

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
            has_developed = hf_count > 0

            bunker_ratio = 0.25
            if bunkers_count < empty_front_length * bunker_ratio:
                self._try_create(fig.Bunker)
                # print("_try_create(fig.Bunker)")
                if self._moves_to_make:
                    # print(self._moves_to_make)
                    return

            for silo in cells.with_owner(self._player) & cells.with_figure(fig.MissileSilo):
                yield from self._try_launch_oreshnik(self._board.coordinates_of(silo))
                # print("_try_launch_oreshnik")
                if self._moves_to_make:
                    # print(self._moves_to_make)
                    return

            target_silos_count = max(1, hf_count // 4)
            if silos_count < target_silos_count:
                self._try_create(fig.MissileSilo)
                # print("_try_create(fig.MissileSilo)")
                if self._moves_to_make:
                    # print(self._moves_to_make)
                    return

            yield from self._try_convert_infantry_to_motorization(.5 if has_developed else .1)
            # print("_try_convert_infantry_to_motorization")
            if self._moves_to_make:
                # print(self._moves_to_make)
                return

            yield from self._try_connect_pullerless_artillery()
            # print("_try_connect_pullerless_artillery")
            if self._moves_to_make:
                # print(self._moves_to_make)
                return

            yield from self._try_upgrade_capitals()
            # print("_try_upgrade_capitals")
            if self._moves_to_make:
                # print(self._moves_to_make)
                return

            yield from self._try_spawn_artillery(math.ceil((infantry_count + motorization_count) * .3) -
                                                 artillery_count)
            # print("_try_spawn_and_connect_artillery")
            if self._moves_to_make:
                # print(self._moves_to_make)
                return

            if has_developed:
                yield from self._try_convert_tanks_to_howitzers(math.floor(tanks_count * _HOWITZERS_TO_TANKS_RATIO) -
                                                                howitzers_count)
                # print("_try_convert_tanks_to_howitzers")
                if self._moves_to_make:
                    # print(self._moves_to_make)
                    return

                yield from self._try_buy_out_private_figures()
                # print("_try_buy_out_private_figures")
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
            yield from self._try_destroy_abandonments()
            if self._moves_to_make:
                # print(self._moves_to_make)
                return

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
        critical = own_cells & cells.with_figure(CRITICAL)
        capitals = cells.with_figure(fig.Capital) & cells.with_owner(self._player)

        match figure:
            case fig.Tank:
                front = Cells({cell for cell in front
                               if self._board.get_neighbors(cell, include_cell=False).with_flag(proto.OnLand)
                              .with_owner(self._player).with_figure(fig.Infantry)})
                if not front:
                    return MISSING
                return self._get_cell_for_armed_figure(front, critical)

            case fig.Infantry:
                tanks = front.with_figure(fig.Tank)
                tanks_neighbors = set[proto.Cell]()
                for cell in tanks:
                    tanks_neighbors |= (self._board
                                        .get_neighbors(cell)
                                        .with_owner(self._player)
                                        .with_figure(fig.Land)
                                        .as_set())

                if tanks_neighbors:
                    return random.choice(list(tanks_neighbors))

                return self._get_cell_for_armed_figure(front, critical)

            case fig.Bunker:
                return self._get_cell_for_bunker(front, critical)

            case fig.TierOneCapital:
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
                    points += len(neighbors & production) * 100

                    if points > max_points:
                        max_points = points
                        target = candidate

                if target is MISSING:
                    return random.choice(empties.as_list())

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
        resources = list(map(type[Resource], _TARGET_RESERVE_RATIO_OF))
        flow = ResourcesGroup()
        for resource in resources:
            for result in self._getting_flow_process(resource):
                yield
                if result is not MISSING:
                    flow += ResourcesGroup.make(resource(result))

        target_reserve = _TARGET_RESERVE_RATIO_OF * cells_count ** .25
        current_reserv = self._player.resources.as_group
        target_flow = (target_reserve - current_reserv) + flow

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

    def _try_upgrade_capitals(self) -> Iterator[None]:
        cells = self._session.cells
        board = self._session.board
        our_cells = cells.with_owner(self._player)

        capitals = our_cells & cells.with_figure(fig.Capital)
        capitals -= cells.with_figure(fig.TallCapital | fig.WideCapital)
        if not capitals:
            return

        distance = fig.WideCapital.FLAGS.get(proto.BuffsNearbyResourceAdders).distance
        for capital in capitals:
            yield
            neighbors = our_cells & DistantNeighborsGetter(capital, board).get_as_far_as(distance)
            figure_to_upgrade_into = (fig.WideCapital
                                      if neighbors.with_figure(PRODUCTION) else
                                      fig.TallCapital)

            move = Conversion(board.coordinates_of(capital),
                              figure_to_upgrade_into)
            if (valid_move := move.validate(self._session)) is not INVALID:
                self._moves_to_make.append(valid_move)

    def _try_destroy_abandonments(self) -> Iterator[None]:
        connections = self._session.pulling_connections
        cells = self._session.cells
        board = self._session.board
        our_cells = cells.with_owner(self._player)

        abandonments = our_cells & cells.with_figure(fig.Abandonment)
        if not abandonments:
            return
        yield
        abandonment = abandonments.any

        infantries = our_cells & cells.with_figure(fig.Infantry | fig.Motorization)
        yield
        infantries = infantries.filter(lambda cell: connections.is_puller(cell.figure) and
                                                    isinstance(connections.get_pullable(cell.figure),
                                                               fig.Artillery) and
                                                    (board.get_neighbors(cell) & our_cells).with_figure(fig.Land))

        is_catastrophy = len(abandonments) >= _CATASTROPHY_ABANDONMENTS_COUNT

        for _ in range(1 if not is_catastrophy else min(len(infantries), len(abandonments))):
            yield

            if not infantries:
                break
            infantry = min(infantries, key=lambda cell: get_distance(board.coordinates_of(cell),
                                                                     board.coordinates_of(abandonment)))
            infantries = infantries.without(infantry)
            artillery = board[self._session.figures.locate(connections.get_pullable(infantry.figure))]
            yield

            target = min(abandonments, key=lambda cell: get_distance(board.coordinates_of(cell),
                                                                     board.coordinates_of(infantry)))
            yield

            move = Attack(board.coordinates_of(artillery),
                          board.coordinates_of(target))
            if (valid_move := move.validate(self._session)) is not INVALID:
                self._moves_to_make.append(valid_move)
                abandonments = abandonments.without(target)
                continue

            yield from self._add_distant_relocation_moves(infantry, target)

    def _try_buy_out_private_figures(self) -> Iterator[None]:
        cells = self._session.cells
        privates = (cells.with_owner(self._player) &
                    cells.with_figure(fig.Settlement | fig.PrivateLightFactory | fig.PrivateHeavyFactory))
        for private in privates:
            yield
            target = _NOT_PRIVATE_VERSION_OF[type(private.figure)]
            move = Conversion(self._board.coordinates_of(private), target)
            if (valid_move := move.validate(self._session)) is not INVALID:
                self._moves_to_make.append(valid_move)

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
                            cells.with_owner(player) & cells.with_figure(CRITICAL)))

        if not targets:
            return
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

    def _try_convert_tanks_to_howitzers(self, amount: int) -> Iterator[None]:
        if amount <= 0:
            return

        cells = self._session.cells
        our_cells = cells.with_owner(self._player)

        tanks = our_cells & cells.with_figure(fig.Tank)
        converted = 0
        for tank in tanks:
            yield
            neighbors = self._board.get_neighbors(tank) & our_cells - cells.not_empty()
            if not neighbors:
                continue
            cell = neighbors.any
            creation = Creation(fig.Artillery, self._board.coordinates_of(cell))
            if (valid_creation := creation.validate(self._session)) is not INVALID:
                converted += 1
                self._moves_to_make.append(valid_creation)
                self._moves_to_make.append(ValidMove(Combination(self._board.coordinates_of(tank),
                                                                 self._board.coordinates_of(cell),
                                                                 fig.Howitzer)))
            if converted >= amount:
                return

    def _try_spawn_artillery(self, amount: int) -> Iterator[None]:
        if amount <= 0:
            return

        cells = self._session.cells
        creatable = fig.Artillery.FLAGS.get(proto.Creatable)

        targets = ((cells.with_owner(self._player) &
                    cells.with_figure(creatable.necessary_neighbor))
                   .filter(lambda cell: self._session.figures_budget
                           .can_spend(cell.figure,
                                      cell.figure.get_cost_of(Creation(fig.Artillery, Vector2Int.zero()))))
                   .filter(lambda cell: bool(self._board
                                             .get_neighbors(cell, include_cell=False)
                                             .with_figure(fig.Land))))
        if not targets:
            return

        for cell, _ in zip(targets, range(amount)):
            yield
            place = (self._board
                     .get_neighbors(cell, include_cell=False)
                     .with_figure(fig.Land)
                     .any)
            make = Creation(fig.Artillery, self._board.coordinates_of(place))
            if (valid_move := make.validate(self._session)) is not INVALID:
                self._moves_to_make.append(valid_move)

    def _try_connect_pullerless_artillery(self) -> Iterator[None]:
        cells = self._session.cells
        connections = self._session.pulling_connections

        artilleries = (cells.with_owner(self._player) &
                       cells.with_figure(fig.Artillery))
        if not artilleries:
            return
        yield

        infantries = ((cells.with_owner(self._player) &
                       cells.with_figure(fig.Infantry))
                      .filter(lambda cell: not connections.is_puller(cell.figure)))
        if not infantries:
            return
        yield

        not_pullable = {artillery for artillery in artilleries
                        if not connections.is_pullable(artillery.figure)}
        if not not_pullable:
            return
        yield

        for cell in not_pullable:
            yield
            places = self._board.get_neighbors(cell).with_owner(self._player).with_figure(fig.Land)
            if not places:
                continue

            infantry = self._get_nearest_to(cell, infantries)
            place = self._get_nearest_to(infantry, places)
            length = len(self._moves_to_make)
            yield from self._add_distant_relocation_moves(infantry, place)
            if len(self._moves_to_make) <= length:
                continue

            connect = PullingInitiation(self._board.coordinates_of(cell), self._board.coordinates_of(place))
            self._moves_to_make.append(ValidMove(connect))

    def _get_target_enemy(self, cell: proto.Cell, *, save_tanks: bool = True) -> proto.Cell | Status:
        neighbors = self._board.get_neighbors(cell, include_cell=False).with_flag(proto.OnLand)
        if not neighbors:
            return MISSING

        targets = neighbors - neighbors.with_owner(self._player)
        targets -= targets.with_flag(proto.CannotBeDestroyed)
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
        to_pull = (cells.with_owner(self._player) &
                   cells.with_figure(fig.Infantry | fig.Motorization | fig.Tank | fig.Howitzer))

        to_pull = Cells(set(filter(lambda cell: self._session
                                   .figures_budget
                                   .can_spend(cell.figure,
                                              cell.figure
                                              .get_cost_of(Relocation(Vector2Int.zero(),
                                                                      Vector2Int.zero()))),
                                   to_pull)))
        if not to_pull:
            return

        tanks = to_pull.with_figure(fig.Tank)
        not_tanks = to_pull - tanks

        for cell in not_tanks:
            yield
            target = self._get_pull_not_tanks_cell(cell)
            if target is MISSING:
                continue

            yield from self._add_distant_relocation_moves(cell, target)
            if self._moves_to_make:
                return

        for cell in tanks:
            yield
            target = self._get_pull_tank_cell(cell)
            if target is MISSING:
                continue

            yield from self._add_distant_relocation_moves(cell, target)
            if self._moves_to_make:
                return

    def _add_distant_relocation_moves(self, cell: proto.Cell, target: proto.Cell) -> Iterator[None]:
        cells = self._session.cells
        path_searcher = PathSearcher(self._board,
                                     cells.with_owner(self._player) -
                                     (cells.not_empty() - cells.at_front) +
                                     Cells({cell, target}),
                                     target)

        path = list[Vector2Int]()
        for path in path_searcher.search_process_from(cell):
            yield
            if path is not None:
                break

        if len(path) < 2:
            return

        if Relocation(path[0], path[1]).validate(self._session) is INVALID:
            return

        for previous, new in zip(path[:-1], path[1:]):
            if not self._board[new].is_empty:
                break

            self._moves_to_make.append(ValidMove(Relocation(previous, new)))

    def _get_pull_not_tanks_cell(self, cell: proto.Cell) -> proto.Cell | Status:
        assert isinstance(cell.figure, fig.Infantry | fig.Motorization | fig.Howitzer)

        cells = self._session.cells
        front = cells.at_front & cells.with_owner(self._player)

        if cell in front:
            return MISSING

        empty_front = front & cells.with_figure(fig.Land)
        if not empty_front:
            empty_front = front

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

    def _try_convert_infantry_to_motorization(self, target_ratio: float) -> Iterator[None]:
        cells = self._session.cells
        infantries = cells.with_owner(self._player) & cells.with_figure(fig.Infantry)
        if not infantries:
            return
        yield

        infantry_count = len(infantries.as_set())
        motorization_count = self._count_of(fig.Motorization)
        to_convert = max(0, math.floor((infantry_count + motorization_count) * target_ratio - motorization_count))
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
            yield
            if (target := self._get_target_enemy(cell)) is MISSING:
                yield
                continue

            move = Assault(self._board.coordinates_of(cell),
                           self._board.coordinates_of(target))
            if (valid_move := move.validate(self._session)) is INVALID:
                continue
            if all((CanCapture in cell.figure.FLAGS,
                    not target.is_empty,
                    type(target.figure) not in _NOT_TO_CAPTURE)):
                self._moves_to_make.append(ValidMove(Capture(move.from_coord,
                                                             move.to_coord)))
            self._moves_to_make.append(valid_move)

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
            neighbors -= neighbors.with_flag(proto.CannotBeDestroyed)
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
        cells = self._session.cells
        artilleries = (cells.with_owner(self._player) &
                       cells.with_figure(fig.Artillery | fig.Howitzer))
        if not artilleries:
            return
        yield

        for artillery in artilleries:
            yield
            neighbors = (DistantNeighborsGetter(artillery, self._board)
                         .get_all_not_farther_than(fig.Artillery.FLAGS.get(proto.CanAttack).max_distance,
                                                   include_cell=False)
                         .with_flag(proto.OnLand))

            abandonments = (neighbors &
                            cells.with_owner(self._player) &
                            cells.with_figure(fig.Abandonment))
            if abandonments:
                target = abandonments.any
                move = Attack(self._board.coordinates_of(artillery),
                              self._board.coordinates_of(target))
                if (valid_move := move.validate(self._session)) is not INVALID:
                    self._moves_to_make.append(valid_move)
                return

            neighbors -= cells.with_owner(self._player)
            neighbors -= cells.with_figure(fig.Land | fig.Abandonment)
            neighbors -= neighbors.with_flag(proto.CannotBeDestroyed)
            if not neighbors:
                continue

            targets = Cells.empty()
            for figure in _ARTILLERY_PRIORITY_LIST:
                targets = neighbors.with_figure(figure)
                if targets:
                    break
            assert targets

            target = max(targets.as_set(), key=lambda cell: cell.hardness(self._board))
            move = Attack(self._board.coordinates_of(artillery),
                          self._board.coordinates_of(target))
            if (valid_move := move.validate(self._session)) is not INVALID:
                self._moves_to_make.append(valid_move)

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
            neighbors = neighbors.filter(lambda cell: type(cell.figure) not in _NOT_TO_CAPTURE)
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
        assert (creatable := figure.FLAGS.get(proto.Creatable)) is not MISSING

        if (cell := self._get_cell_for(figure)) is MISSING:
            return

        cells = self._session.cells
        if creatable.necessary_neighbor is not MISSING:
            targets = ((cells.with_owner(self._player) &
                        cells.with_figure(creatable.necessary_neighbor))
                       .filter(lambda cell: self._session.figures_budget
                               .can_spend(cell.figure,
                                          cell.figure.get_cost_of(Creation(figure, Vector2Int.zero()))))
                       .filter(lambda cell: bool(self._board
                                                 .get_neighbors(cell, include_cell=False)
                                                 .with_figure(fig.Land))))
            if not targets:
                return

            cell = (self._board
                    .get_neighbors(self._get_nearest_to(cell, targets), include_cell=False)
                    .with_figure(fig.Land)
                    .any)

        if not self._can_create(figure, cell):
            return

        valid_move = self._create(figure, cell)
        self._moves_to_make.append(valid_move)

    def _count_of(self, figure: type[fig.Figure]) -> int:
        cells = self._session.cells
        res = len((cells.with_owner(self._player) &
                   cells.with_figure(figure)).as_set())
        return res

    def _get_nearest_to(self, target: proto.Cell, candidates: proto.Cells) -> proto.Cell:
        assert candidates

        coord_of = self._board.coordinates_of
        return min(candidates, key=lambda cell: get_distance(coord_of(target), coord_of(cell)))

    def _min_sqrt_distance_cell(self, candidates: proto.Cells, targets: proto.Cells) -> proto.Cell:
        coord_of = self._board.coordinates_of
        return min(candidates, key=lambda front_cell: sum((coord_of(front_cell) -
                                                           coord_of(production_cell)).length ** .25
                                                          for production_cell in targets))
