from abc import ABC
from typing import Callable

from attrs import frozen, field

from appearance.input.clicks_catcher.click import Buttons
from appearance.input.clicks_catcher.layers.board_layer import BoardLayer
from core.moves import Relocation, Capture
from core.protocols import Move, Board, ValidMove
from mathematics.vector import Vector2Int
from observer import Event
from observer import ToEventSubscriber
from statuses import Status, INVALID, CAN_BECOME_CORRECT


@frozen
class MovesInputer:
    @classmethod
    def make(cls, board_layer: BoardLayer, board: Board) -> "MovesInputer":
        reader = InputActionsReader.make(board_layer)
        inputer = cls(reader, MoveReaders(board), board)
        reader.move_was_raed.subscribe(inputer._on_action_was_read)
        return inputer

    _move_was_raed: Event[ValidMove, None] = field(init=False, factory=Event)

    _actions_reader: "InputActionsReader"
    _move_reader: "MoveReaders"
    _board: Board

    @property
    def move_was_raed(self) -> "ToEventSubscriber[ValidMove, None]":
        return self._move_was_raed.subscriber

    def _on_action_was_read(self, action: "InputAction") -> None:
        while actions := self._actions_reader.actions:
            results = list(map(lambda reader: reader(actions),
                               self._move_reader.readers))

            moves = [result for result in results if isinstance(result, ValidMove)]
            assert len(moves) < 2

            if moves:
                move = moves[0]
                self._move_was_raed.invoke(move)
                self._actions_reader.clear()
                return

            if CAN_BECOME_CORRECT in results:
                break

            self._actions_reader.pop()


@frozen
class MoveReaders:
    _board: Board

    @property
    def readers(self) -> list[Callable[[list["InputAction"]], ValidMove | Status]]:
        return [
            self._try_read_relocation_move,
            self._try_read_capture_move,
        ]

    def _try_read_relocation_move(self, actions: list["InputAction"]) -> ValidMove | Status:
        match actions:
            case [CellClickAction(coord=from_coord,
                                  buttons=Buttons(is_left=True)),
                  CellClickAction(coord=to_coord,
                                  buttons=Buttons(is_right=True))]:
                return Relocation(from_coord, to_coord).validate(self._board)

            case [CellClickAction(buttons=Buttons(is_left=True))]:
                return CAN_BECOME_CORRECT

            case _:
                return INVALID

    def _try_read_capture_move(self, actions: list["InputAction"]) -> ValidMove | Status:
        match actions:
            case [CellClickAction(coord=from_coord,
                                  buttons=Buttons(is_left=True)),
                  CellClickAction(coord=to_coord,
                                  buttons=Buttons(is_right=True))]:
                return Capture(from_coord, to_coord).validate(self._board)

            case [CellClickAction(buttons=Buttons(is_left=True))]:
                return CAN_BECOME_CORRECT

            case _:
                return INVALID


@frozen
class InputActionsReader:
    @classmethod
    def make(cls, board_layer: BoardLayer) -> "InputActionsReader":
        reader = cls()
        board_layer.cell_was_clicked_left.subscribe(reader._on_cell_was_clicked_left)
        board_layer.cell_was_clicked_right.subscribe(reader._on_cell_was_clicked_right)
        board_layer.cell_was_clicked_middle.subscribe(reader._on_cell_was_clicked_middle)
        return reader

    _action_was_raed: Event["InputAction", None] = field(init=False, factory=Event)

    _actions: list["InputAction"] = field(init=False, factory=list)

    @property
    def move_was_raed(self) -> "ToEventSubscriber[InputAction, None]":
        return self._action_was_raed.subscriber

    @property
    def actions(self) -> list["InputAction"]:
        return list(self._actions)

    def clear(self) -> None:
        self._actions.clear()

    def pop(self) -> None:
        self._actions.pop(0)

    def _on_cell_was_clicked_left(self, coord: Vector2Int) -> None:
        action = CellClickAction(coord, Buttons(is_left=True))
        self._actions.append(action)
        self._action_was_raed.invoke(action)

    def _on_cell_was_clicked_right(self, coord: Vector2Int) -> None:
        action = CellClickAction(coord, Buttons(is_right=True))
        self._actions.append(action)
        self._action_was_raed.invoke(action)

    def _on_cell_was_clicked_middle(self, coord: Vector2Int) -> None:
        action = CellClickAction(coord, Buttons(is_middle=True))
        self._actions.append(action)
        self._action_was_raed.invoke(action)


class InputAction(ABC):
    ...


@frozen
class CellClickAction(InputAction):
    coord: Vector2Int
    buttons: Buttons
