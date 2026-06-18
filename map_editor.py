from typing import Callable, Iterator

from attrs import define
import arcade as arc

import core.protocols as proto
from appearance.input.moves_inputer.input_actions import CellClickAction
from appearance.protocols import InputAction, MouseButtons, InputActionsReader, InputState
from core.cells import Cells
from mathematics.vector import Vector2Int
from my_types import ContextManager
from statuses import MISSING, Status
import core.figures.figure as fig

FILL_KEY = arc.key.LSHIFT

Transform = tuple[str, Callable[[Vector2Int], None]]


@define
class MapEditor:
    @classmethod
    def make(cls,
             input_state: InputState,
             session: proto.GameSession,
             actions_reader: InputActionsReader,
             on_changed_cell_owner: Callable[[Vector2Int], None],
             multiple_cells_change: Callable[[Cells], ContextManager[None]]) -> "MapEditor":
        transforms = list[Transform]()
        self = cls(input_state, session, on_changed_cell_owner, multiple_cells_change, transforms, "water")
        actions_reader.action_was_read.subscribe(self._on_action_was_read)

        transforms.append(("water", lambda coord: self._change_owner_to(coord, MISSING)))
        transforms.append(("empty land", lambda coord: self._change_figure(coord, fig.Land)))
        transforms.append(("town", lambda coord: self._change_figure(coord, fig.Town)))
        transforms.append(("light factory", lambda coord: self._change_figure(coord, fig.LightFactory)))
        transforms.append(("heavy factory", lambda coord: self._change_figure(coord, fig.HeavyFactory)))
        transforms.append(("capital", lambda coord: self._change_figure(coord, fig.Capital)))
        transforms.append(("bunker", lambda coord: self._change_figure(coord, fig.Bunker)))
        transforms.append(("silo", lambda coord: self._change_figure(coord, fig.MissileSilo)))
        transforms.append(("artillery", lambda coord: self._change_figure(coord, fig.Artillery)))
        transforms.append(("infantry", lambda coord: self._change_figure(coord, fig.Infantry)))
        transforms.append(("motorization", lambda coord: self._change_figure(coord, fig.Motorization)))
        transforms.append(("tank", lambda coord: self._change_figure(coord, fig.Tank)))
        transforms.append(("settlement", lambda coord: self._change_figure(coord, fig.Settlement)))
        transforms.append(("plf", lambda coord: self._change_figure(coord, fig.PrivateLightFactory)))
        transforms.append(("phf", lambda coord: self._change_figure(coord, fig.PrivateHeavyFactory)))

        for player in session.master.players:
            transforms.append(self._make_set_player_transform(player))

        return self

    _input_state: InputState
    _session: proto.GameSession
    _on_changed_cell_owner: Callable[[Vector2Int], None]
    _multiple_cells_change: Callable[[Cells], ContextManager[None]]

    _transforms: list[Transform]
    _transform: str

    _process: Iterator[None] | Status = MISSING

    @property
    def transforms(self) -> list[str]:
        return list(map(lambda pair: pair[0], self._transforms))

    def set(self, transform: str) -> None:
        assert transform in dict(self._transforms).keys()

        self._transform = transform

    def update(self) -> None:
        if self._process is not MISSING:
            next(self._process)

    def _make_set_player_transform(self, player: proto.Player) -> Transform:
        return player.data.name, lambda coord: self._change_owner_to(coord, player)

    def _on_action_was_read(self, action: InputAction, _: bool) -> None:
        match action:
            case CellClickAction(coord=click_coord, buttons=MouseButtons(is_left=True)):
                ...
            case _:
                return

        cells_to_transform = (self._session.board.get_region_with_same_owner(self._session.board[click_coord])
                              if FILL_KEY in self._input_state.pressed_keys else
                              Cells({self._session.board[click_coord]}))

        self._process = self._get_transform_process(cells_to_transform)

    def _get_transform_process(self, cells: Cells) -> Iterator[None]:
        with self._multiple_cells_change(cells):
            for cell in cells:
                self._make_transform(self._session.board.coordinates_of(cell))

        self._process = MISSING
        yield

    def _make_transform(self, coord: Vector2Int) -> None:
        dict(self._transforms)[self._transform](coord)

    def _change_owner_to(self, coord: Vector2Int, player: proto.Player | Status) -> None:
        cell = self._session.board[coord]
        if cell.owner == player:
            return

        if self._handle_surface_type_change(player, cell):
            return

        cell.change_owner_to(player)
        self._on_changed_cell_owner(coord)

    def _handle_surface_type_change(self, player: proto.Player | Status, cell: proto.Cell) -> bool:
        coord = self._session.board.coordinates_of(cell)

        if player is MISSING and not cell.figure.is_on_land():
            return True

        if player is MISSING and cell.figure.is_on_land():
            if not cell.is_empty:
                self._session.figures.remove(cell.figure)
            cell.turn_into_water()
            self._on_changed_cell_owner(coord)
            return True

        if player is not MISSING and not cell.figure.is_on_land():
            if not cell.is_empty:
                self._session.figures.remove(cell.figure)
            cell.turn_into_land(player)
            self._on_changed_cell_owner(coord)
            return True

        return False

    def _change_figure(self, coord: Vector2Int, target: type[proto.Figure]) -> None:
        cell = self._session.board[coord]
        if target.is_on_land() != cell.figure.is_on_land():
            return

        if not cell.is_empty:
            self._session.figures.remove(cell.figure)

        if proto.Empty not in target.FLAGS:
            self._session.figures.add(target, coord)
