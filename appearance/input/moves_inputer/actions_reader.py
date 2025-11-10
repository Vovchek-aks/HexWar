from attrs import frozen, field

from appearance.input.clicks_catcher.click import Click
from mathematics.vector import Vector2Int
from observer import Event, OnEventSubscriber
from appearance.input.moves_inputer.input_actions import InputAction, CellClickAction, NullClickAction
import appearance.protocols as proto


@frozen
class InputActionsReader(proto.InputActionsReader):
    @classmethod
    def make(cls, board_layer: proto.BoardLayer, null_layer: proto.WholeScreenLayer) -> "InputActionsReader":
        reader = cls()

        board_layer.cell_was_clicked.subscribe(reader._on_cell_was_clicked)

        null_layer.was_clicked.subscribe(reader._on_null_click)

        return reader

    _action_was_raed: Event[InputAction, None] = field(init=False, factory=Event)

    _actions: list[InputAction] = field(init=False, factory=list)

    @property
    def action_was_raed(self) -> OnEventSubscriber[InputAction, None]:
        return self._action_was_raed.subscriber

    @property
    def actions(self) -> list[InputAction]:
        return list(self._actions)

    def clear(self) -> None:
        self._actions.clear()

    def pop(self) -> None:
        self._actions.pop(0)

    def _add_action(self, action: InputAction) -> None:
        self._actions.append(action)
        self._action_was_raed.invoke(action)

    def _on_cell_was_clicked(self, coord: Vector2Int, buttons: proto.MouseButtons) -> None:
        self._add_action(CellClickAction(coord, buttons))

    def _on_null_click(self, click: Click) -> None:
        self._add_action(NullClickAction(click))
