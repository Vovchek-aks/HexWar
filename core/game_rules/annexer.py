import random
from typing import Iterator, Callable

from attrs import frozen

from mathematics.vector import Vector2Int
from my_random import temporarily_seed
from .game_rule import GameRule
import core.protocols as proto
import core.figures.figure as fig
from ..cells import Cells
from my_types import ContextManager


@frozen
class Annexer(GameRule):
    _multiple_cells_change: Callable[[Cells], ContextManager[None]]
    _on_changed_cell_owner: Callable[[Vector2Int], None]
    _annexation_map: proto.AnnexationMapUpdater

    def on_turn_end(self, session: proto.GameSession) -> Iterator[None]:
        board = session.board
        player = session.master.current_player
        map_updater = self._annexation_map

        map_updater.push(player)
        while map_updater.is_about_to_be_updated(player):
            yield

        for region in (map_updater.map.get_cells_to_annex_of(player).split(board)):
            yield
            self.annex(session, region)
            for player in region.players():
                map_updater.push(player)

    def annex(self, session: proto.GameSession, region: Cells) -> None:
        cells = session.cells
        manned = region & cells.with_figure(fig.Infantry | fig.Motorization)
        for cell in manned:
            session.figures.remove(cell.figure)

        connections = session.pulling_connections
        for cell in region & cells.with_flag(proto.Pullable):
            figure = cell.figure
            if not connections.is_pullable(figure):
                return
            connections.unregister(connections.get_connected(figure), figure)
        for cell in region & cells.with_flag(proto.CanPull):
            figure = cell.figure
            if not connections.is_puller(figure):
                return
            connections.unregister(figure, connections.get_connected(figure))

        with self._multiple_cells_change(region):
            while region:
                annexed = self._annex_boundry(region, session.board)
                if not annexed:
                    break
                region -= annexed

        for cell in region:
            cells.update(cell)

    def _annex_boundry(self, region: Cells, board: proto.Board) -> Cells:
        to_annex = list[tuple[proto.Cell, proto.Player]]()
        boundry = region.at_inner_boundry(board)
        for cell in boundry:
            neighbors = (board.get_neighbors(cell) - region).with_flag(proto.OnLand)
            neighbors -= neighbors.with_owner(cell.owner)
            if not neighbors:
                continue

            with temporarily_seed(str(board.coordinates_of(cell))):
                annexer = random.choice(neighbors.as_list()).owner
            to_annex.append((cell, annexer))

        for cell, annexer in to_annex:
            cell.change_owner_to(annexer)
            self._on_changed_cell_owner(board.coordinates_of(cell))

        return Cells({pair[0] for pair in to_annex})
