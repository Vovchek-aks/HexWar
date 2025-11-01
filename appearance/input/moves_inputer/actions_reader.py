from attrs import frozen, field

from appearance.input.clicks_catcher.click import Buttons
from appearance.input.clicks_catcher.layers.board_layer import BoardLayer
from mathematics.vector import Vector2Int
from observer import Event, ToEventSubscriber
from appearance.input.moves_inputer.input_actions import InputAction, CellClickAction


@frozen
class InputActionsReader:
    @classmethod
    def make(cls, board_layer: BoardLayer) -> "InputActionsReader":
        reader = cls()
        board_layer.cell_was_clicked_left.subscribe(reader._on_cell_was_clicked_left)
        board_layer.cell_was_clicked_right.subscribe(reader._on_cell_was_clicked_right)
        board_layer.cell_was_clicked_middle.subscribe(reader._on_cell_was_clicked_middle)
        return reader

    _action_was_raed: Event[InputAction, None] = field(init=False, factory=Event)

    _actions: list[InputAction] = field(init=False, factory=list)

    @property
    def move_was_raed(self) -> "ToEventSubscriber[InputAction, None]":
        return self._action_was_raed.subscriber

    @property
    def actions(self) -> list[InputAction]:
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
