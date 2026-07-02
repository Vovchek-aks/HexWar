import random
from math import ceil
from typing import Callable, Iterator

from attrs import frozen

from core import protocols as proto
from core.cells import Cells
from core.distant_neighbors_getter import DistantNeighborsGetter
from core.figures import figure as fig
from mathematics.vector import Vector2Int
from my_types import ContextManager

FROM_FRONT_TO_BUNKER_MAX_DISTANCE = 3

PRIVATES_RATIO = .2
PRIVATES_DECREASE_FROM_CAPITALS_RATIO = 0
PRIVATES_SPAWN_SPEED_MULTIPLIER = .1
PRIVATES_WEIGHTS = {
    fig.Settlement: 1,
    fig.PrivateLightFactory: .3,
    fig.PrivateHeavyFactory: .05,
}


@frozen
class ByGameRulesSessionChanger(proto.ByGameRulesSessionChanger):
    _session: proto.GameSession
    _annexation_map_updater: proto.AnnexationMapUpdater
    _multiple_cells_change: Callable[[Cells], ContextManager[None]]
    _on_changed_cell_owner: Callable[[Vector2Int], None]

    @property
    def _board(self) -> proto.Board:
        return self._session.board

    def on_turn_start(self) -> None:
        board = self._session.board
        player = self._session.master.current_player
        cells_cache = self._session.cells
        figures = self._session.figures
        cells = cells_cache.with_owner(player)

        to_update = cells & cells_cache.with_flag(proto.UpdatableOnTurnStart)
        priority_order = sorted(to_update, key=lambda cell: cell.figure.FLAGS.get(proto.UpdatableOnTurnStart).priority)

        for cell in priority_order:
            cell.figure.FLAGS.get(proto.UpdatableOnTurnStart).update(board.coordinates_of(cell), self._session)

        front = cells & cells_cache.at_front
        for bunker in cells & cells_cache.with_figure(fig.Bunker):
            neighbors = (DistantNeighborsGetter(bunker, board)
                         .get_all_not_farther_than(FROM_FRONT_TO_BUNKER_MAX_DISTANCE, include_cell=True))
            if not neighbors & front:
                figures.remove(bunker.figure)
                figures.add(fig.Abandonment, board.coordinates_of(bunker))


    def on_turn_end(self) -> Iterator[None]:
        player = self._session.master.current_player
        cells = self._session.cells.with_owner(player)

        yield from self._process_turn_end_annexations(player)

        yield from self._spawn_private_figures(cells)

        yield from self._process_into_itself_other_turners(cells)

    def annex(self, region: Cells) -> None:
        manned = region & self._session.cells.with_figure(fig.Infantry | fig.Motorization)
        for cell in manned:
            self._session.figures.remove(cell.figure)

        with self._multiple_cells_change(region):
            while region:
                annexed = self._annex_boundry(region)
                if not annexed:
                    break
                region -= annexed

        for cell in region:
            self._session.cells.update(cell)

    def _process_turn_end_annexations(self, player: proto.Player) -> Iterator[None]:
        map_updater = self._annexation_map_updater
        map_updater.push(player)
        while map_updater.is_about_to_be_updated(player):
            yield
        for region in (map_updater.map.get_cells_to_annex_of(player).split(self._session.board)):
            yield
            self.annex(region)
            for player in region.players():
                map_updater.push(player)
        return player

    def _spawn_private_figures(self, player_cells: Cells) -> Iterator[None]:
        cells = self._session.cells
        empties = player_cells - cells.not_empty()
        privates = player_cells.with_flag(proto.Private)

        target_count = ((len(empties) + len(privates)) * PRIVATES_RATIO -
                        len(player_cells & cells.with_figure(fig.Capital)) * PRIVATES_DECREASE_FROM_CAPITALS_RATIO)
        if target_count <= 0:
            return
        yield
        progress = len(privates) / target_count
        to_spawn = ceil(target_count * (1 - progress) * PRIVATES_SPAWN_SPEED_MULTIPLIER)

        private_figures, weights = zip(*PRIVATES_WEIGHTS.items())  # Jaxx22
        for cell in random.sample(empties.as_list(), to_spawn):
            yield
            figure: type[fig.Figure] = random.choices(private_figures, weights=weights)[0]
            self._session.figures.add(figure, self._session.board.coordinates_of(cell))

    def _process_into_itself_other_turners(self, player_cells: Cells) -> Iterator[None]:
        figures = self._session.figures
        board = self._session.board
        turners = player_cells & self._session.cells.with_flag(proto.TurnsOthersIntoItself)
        yield
        for turner in turners:
            coord = board.coordinates_of(turner)
            for cell in turner.figure.FLAGS.get(proto.TurnsOthersIntoItself).get_targets(coord, self._session):
                figures.remove(cell.figure)
                figures.add(type(turner.figure), board.coordinates_of(cell))

    def _discard_regions_with(self, targets: Cells, cells: Cells) -> Cells:
        while targets:
            target = targets.any
            targets = targets.without(target)

            region = self._board.get_region_with_same_owner(target)
            cells -= region
            targets -= region

        return cells

    def _annex_boundry(self, region: Cells) -> Cells:
        to_annex = list[tuple[proto.Cell, proto.Player]]()
        boundry = region.at_inner_boundry(self._board)
        for cell in boundry:
            neighbors = (self._board.get_neighbors(cell) - region).with_flag(proto.OnLand)
            neighbors -= neighbors.with_owner(cell.owner)
            if not neighbors:
                continue

            annexer = random.choice(neighbors.as_list()).owner
            to_annex.append((cell, annexer))

        for cell, annexer in to_annex:
            cell.change_owner_to(annexer)
            self._on_changed_cell_owner(self._board.coordinates_of(cell))

        return Cells({pair[0] for pair in to_annex})
