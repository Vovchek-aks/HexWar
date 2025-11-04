from attrs import frozen, field

from appearance.input.clicks_catcher.click import Buttons, Click
from appearance.input.clicks_catcher.layers.board_layer import BoardLayer
from appearance.input.clicks_catcher.layers.whole_screen_layer import WholeScreenLayer
from mathematics.vector import Vector2Int
from observer import Event, OnEventSubscriber
from appearance.input.moves_inputer.input_actions import InputAction, CellClickAction, NullClickAction


@frozen
class InputActionsReader:
    @classmethod
    def make(cls, board_layer: BoardLayer, null_layer: WholeScreenLayer) -> "InputActionsReader":
        reader = cls()

        board_layer.cell_was_clicked_left.subscribe(reader._on_cell_was_clicked_left)
        board_layer.cell_was_clicked_right.subscribe(reader._on_cell_was_clicked_right)
        board_layer.cell_was_clicked_middle.subscribe(reader._on_cell_was_clicked_middle)

        null_layer.click_happened.subscribe(reader._on_null_click)

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

    def _on_cell_was_clicked_left(self, coord: Vector2Int) -> None:
        self._add_action(CellClickAction(coord, Buttons(is_left=True)))

    def _on_cell_was_clicked_right(self, coord: Vector2Int) -> None:
        self._add_action(CellClickAction(coord, Buttons(is_right=True)))

    def _on_cell_was_clicked_middle(self, coord: Vector2Int) -> None:
        self._add_action(CellClickAction(coord, Buttons(is_middle=True)))

    def _on_null_click(self, click: Click) -> None:
        self._add_action(NullClickAction(click))
