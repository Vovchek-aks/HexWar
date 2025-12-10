from attrs import define, field

from appearance.input.clicks_catcher.click import MouseButtons
from appearance.input.moves_inputer.actions_reader import InputActionsReader
from appearance.input.moves_inputer.input_actions import InputAction, NullClickAction, CellClickAction
from core.moves.relocations import Relocation, Assault
from core.protocols import ValidMove, MovesMaker, Master
from mathematics.vector import Vector2Int
from observer import Event, OnEventSubscriber
from statuses import Status, MISSING
import appearance.protocols as proto


@define
class CellSelector(proto.CellSelector):
    @classmethod
    def make(cls,
             actions_reader: InputActionsReader,
             moves_maker: MovesMaker,
             master: Master) -> "CellSelector":
        selector = cls(master)

        actions_reader.action_was_read.subscribe(selector._on_action_was_read)
        moves_maker.board_move_was_made.subscribe(selector._on_board_move_was_made)

        return selector

    _master: Master

    _cell_was_selected: Event[Vector2Int, None] = field(init=False, factory=Event)
    _cell_was_unselected: Event[None] = field(init=False, factory=Event)

    _cell_coord: Vector2Int | Status = field(init=False, default=MISSING)

    @property
    def cell_was_selected(self) -> OnEventSubscriber[Vector2Int, None]:
        return self._cell_was_selected.subscriber

    @property
    def cell_was_unselected(self) -> OnEventSubscriber[None]:
        return self._cell_was_unselected.subscriber

    def get_coord(self) -> Vector2Int | Status:
        return self._cell_coord

    def _on_action_was_read(self, action: InputAction, _: bool) -> None:
        match action:
            case CellClickAction(buttons=MouseButtons(is_left=True), coord=coord):
                self._select_cell(coord)
            case NullClickAction():
                self._unselect_cell()

    def _on_board_move_was_made(self, move: ValidMove) -> None:
        if not self._master.current_player.need_ui:
            return

        match move.move:
            case Relocation(to_coord=coord) | Assault(to_coord=coord):
                self._select_cell(coord)

    def _select_cell(self, coord: Vector2Int) -> None:
        self._cell_coord = coord
        self._cell_was_selected.invoke(coord)

    def _unselect_cell(self) -> None:
        self._cell_coord = MISSING
        self._cell_was_unselected.invoke()
