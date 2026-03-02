from attrs import frozen, field

from appearance.input.clicks_catcher.click import Click
from mathematics.vector import Vector2Int
from observer import Event, OnEventSubscriber
from appearance.input.moves_inputer.input_actions import InputAction, CellClickAction, NullClickAction, \
    ButtonPressAction
import appearance.protocols as proto


@frozen
class InputActionsReader(proto.InputActionsReader):
    @classmethod
    def make(cls,
             board_layer: proto.BoardLayer,
             null_layer: proto.WholeScreenLayer,
             button_press_action_happened: OnEventSubscriber[ButtonPressAction, None]) -> "InputActionsReader":
        reader = cls()

        board_layer.cell_was_clicked.subscribe(reader._on_cell_was_clicked)
        null_layer.was_clicked.subscribe(reader._on_null_click)
        button_press_action_happened.subscribe(reader._on_button_press_action_happened)

        return reader

    _action_was_read: Event[InputAction, bool, None] = field(init=False, factory=Event)
    _action_was_removed: Event[InputAction, bool, None] = field(init=False, factory=Event)

    _actions: list[InputAction] = field(init=False, factory=list)

    @property
    def action_was_read(self) -> OnEventSubscriber[InputAction, bool, None]:
        return self._action_was_read.subscriber

    @property
    def action_was_removed(self) -> OnEventSubscriber[InputAction, bool, None]:
        return self._action_was_removed.subscriber

    @property
    def actions(self) -> list[InputAction]:
        return list(self._actions)

    def clear(self) -> None:
        while self._actions:
            self.pop()

    def pop(self) -> InputAction:
        action = self._actions.pop(0)
        self._on_action_removed(action)
        return action

    def _add_action(self, action: InputAction) -> None:
        is_first = not any(isinstance(action, type(read)) for read in self.actions)
        self._actions.append(action)
        self._action_was_read.invoke(action, is_first)

    def _on_action_removed(self, action: InputAction) -> None:
        is_last = not any(isinstance(action, type(read)) for read in self.actions)
        self._action_was_removed.invoke(action, is_last)

    def _on_cell_was_clicked(self, coord: Vector2Int, buttons: proto.MouseButtons) -> None:
        self._add_action(CellClickAction(coord, buttons))

    def _on_null_click(self, click: Click) -> None:
        self._add_action(NullClickAction(click))

    def _on_button_press_action_happened(self, action: ButtonPressAction) -> None:
        self._add_action(action)
