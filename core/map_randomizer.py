import random
from contextlib import contextmanager
from typing import Iterator, Callable

from attrs import frozen

import core.protocols as proto
from appearance.graphics.colors import get_colors, Color
from core.figures.figures_flags import Terrain, ALL_TERRAINS
from core.game_rules import Annexer
from core.game_session import GameSession
from core.master import Master
from core.player import Player, PlayerData
from files import read_random_bot_names
from game_session_saver import GameSessionSaver, GameSessionLoader
from mathematics.vector import Vector2Int
import core.figures.figure as fig


@frozen
class MapRandomizer:
    @classmethod
    def make(cls,
             session: proto.GameSession,
             make_player_inputer: Callable[[], proto.PlayerInputer]) -> "MapRandomizer":
        session.figures.figure_was_added_at.subscribe(lambda _, coord: session.cells.update(session.board[coord]))
        session.figures.figure_was_removed.subscribe(lambda _, coord: session.cells.update(session.board[coord]))
        annexer = Annexer(no_context_manager,
                          lambda coord: session.cells.update(
                              session.board[coord]),
                          ...)
        return cls(session, annexer, make_player_inputer)

    _session: proto.GameSession
    _annexer: Annexer
    _make_player_inputer: Callable[[], proto.PlayerInputer]

    def get_randomized(self,
                       players_count: int,
                       start_resources: proto.ResourcesGroup,
                       town_per_player: int,
                       ups: int) -> proto.GameSession:
        self._remove_all_figures()
        player = self._fill_with_one_player()
        players = self._add_random_players(player, players_count)
        self._annexer.annex(self._session, self._session.cells.with_owner(player))
        self._spawn_towns_and_get_resources(players, town_per_player, start_resources)
        session = GameSession(Master(players),
                              self._session.board,
                              self._session.figures_budget,
                              self._session.pulling_connections,
                              self._session.cells,
                              self._session.figures)
        session = GameSessionLoader(GameSessionSaver(session).get_json(), ups).load()
        return session

    def _remove_all_figures(self) -> None:
        for cell in self._session.cells.not_empty():
            if proto.TerrainKind in cell.figure.FLAGS:
                continue

            self._session.figures.remove(cell.figure)

    def _fill_with_one_player(self) -> proto.Player:
        player = self._session.master.current_player
        for cell in (self._session.cells.get_all_players() -
                     self._session.cells.with_owner(player)):
            cell.change_owner_to(player)
            self._session.cells.update(cell)
        return player

    def _add_random_players(self, player: proto.Player, players_count: int) -> list[proto.Player]:
        names: list[str] = random.sample(read_random_bot_names(), players_count)
        cells_cache = self._session.cells
        cells = random.sample((cells_cache.with_figure(fig.Land) -
                               cells_cache.at_terrain(*ALL_TERRAINS)).as_list(), players_count)
        coords = map(self._session.board.coordinates_of, cells)
        colors = get_colors(players_count, lightness=.7, deepness=.6)

        players = list[proto.Player]()
        for name, coord, color in zip(names, coords, colors):
            players.append(self._add_player(name, coord, color))

        return players

    def _add_player(self, name: str, coord: Vector2Int, color: Color) -> proto.Player:
        player = Player(PlayerData(color, name), self._make_player_inputer())

        self._session.board[coord].change_owner_to(player)
        self._session.figures.add(fig.TierOneCapital, coord)

        return player

    def _spawn_towns_and_get_resources(self,
                                       players: list[proto.Player],
                                       town_per_player: int,
                                       start_resources: proto.ResourcesGroup) -> None:
        cells_cache = self._session.cells
        not_allowed = (cells_cache.not_empty()
                       + cells_cache.at_terrain(*fig.Town.FLAGS.get(proto.WithRestrictedTerrainKinds).terrain_kinds))
        for player in players:
            player.resources.add(start_resources)

            cells = cells_cache.with_owner(player) - not_allowed
            if not cells:
                continue

            targets: list[proto.Cell] = random.sample(cells.as_list(), min(town_per_player, len(cells) - 1))
            for cell in targets:
                coord = self._session.board.coordinates_of(cell)
                self._session.figures.add(fig.Town, coord)


@contextmanager
def no_context_manager(_: proto.Cells) -> Iterator[None]:
    yield
