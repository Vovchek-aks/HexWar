from attrs import define, field

from appearance.game_engine.game_engine_arc.window import Window
from appearance.input.clicks_catcher.click import Click
from mathematics.vector import Vector2

KEYS = set[int]


@define
class InputState:
    @classmethod
    def make(cls, window: Window) -> "InputState":
        self = cls()
        window.mouse_has_moved.subscribe(self._on_mouse_has_moved)
        window.keyboard_state_changed.subscribe(self._on_keyboard_state_changed)
        window.click_was_made.subscribe(self._on_click_was_made)
        window.mouse_wheel_has_moved.subscribe(self._on_mouse_wheel_has_moved)
        window.update_finished.subscribe(self._on_update_finished)
        window.update_started.subscribe(self._on_update_started)
        return self

    _dt: float = field(init=False, default=0)
    _mouse_position: Vector2 = field(init=False, factory=Vector2.zero)
    _pressed_keys: KEYS = field(init=False, factory=KEYS)
    _last_frame_clicks: list[Click] = field(init=False, factory=list)
    _last_frame_mouse_wheel_delta: float = field(init=False, default=0)

    @property
    def dt(self) -> float:
        return self._dt

    @property
    def mouse_position(self) -> Vector2:
        return self._mouse_position.copy()

    @property
    def pressed_keys(self) -> KEYS:
        return self._pressed_keys.copy()

    @property
    def last_frame_clicks(self) -> list[Click]:
        return self._last_frame_clicks.copy()

    @property
    def last_frame_mouse_wheel_delta(self) -> float:
        return self._last_frame_mouse_wheel_delta

    def _on_mouse_has_moved(self, position: Vector2) -> None:
        self._mouse_position = position

    def _on_keyboard_state_changed(self, keys: KEYS) -> None:
        self._pressed_keys = keys

    def _on_click_was_made(self, click: Click) -> None:
        self._last_frame_clicks.append(click)

    def _on_mouse_wheel_has_moved(self, delta: float) -> None:
        self._last_frame_mouse_wheel_delta += delta

    def _on_update_started(self, dt: float) -> None:
        self._dt = dt

    def _on_update_finished(self, _: float) -> None:
        self._last_frame_clicks.clear()
        self._last_frame_mouse_wheel_delta = 0
