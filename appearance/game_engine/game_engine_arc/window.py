from pathlib import Path

import arcade as arc
from pyglet.image import load

from mathematics.vector import Vector2Int, Vector2
from appearance.input.clicks_catcher.click import Click, MouseButtons
from observer import Event, OnEventSubscriber

ICON_FILE = Path("data") / "sprites" / "icon.png"


class Window(arc.Window):
    def __init__(self, ups: float, is_fullscreen: bool, title: str, screen_shape: Vector2Int) -> None:
        dt = 1 / ups
        super().__init__(screen_shape.x,
                         screen_shape.y,
                         title,
                         vsync=True,
                         samples=2,
                         update_rate=dt,
                         fixed_rate=dt,
                         fullscreen=is_fullscreen)
        self.background_color = arc.color.BLACK
        self.set_icon(load(str(ICON_FILE)))

        self._pressed_keys = set[int]()

        self._fixed_update_started = Event[float, None]()
        self._fixed_update_finished = Event[float, None]()
        self._update_started = Event[float, None]()
        self._update_finished = Event[float, None]()
        self._draw = Event[None]()

        self._click_was_made = Event[Click, None]()
        self._mouse_has_moved = Event[Vector2, None]()
        self._mouse_wheel_has_moved = Event[float, None]()
        self._keyboard_state_changed = Event[set[int], None]()

    @property
    def fixed_update_started(self) -> OnEventSubscriber[float, None]:
        return self._fixed_update_started.subscriber

    @property
    def fixed_update_finished(self) -> OnEventSubscriber[float, None]:
        return self._fixed_update_finished.subscriber

    @property
    def update_started(self) -> OnEventSubscriber[float, None]:
        return self._update_started.subscriber

    @property
    def update_finished(self) -> OnEventSubscriber[float, None]:
        return self._update_finished.subscriber

    @property
    def draw_event(self) -> OnEventSubscriber[None]:
        return self._draw.subscriber

    @property
    def click_was_made(self) -> OnEventSubscriber[Click, None]:
        return self._click_was_made.subscriber

    @property
    def mouse_has_moved(self) -> OnEventSubscriber[Vector2, None]:
        return self._mouse_has_moved.subscriber

    @property
    def mouse_wheel_has_moved(self) -> OnEventSubscriber[float, None]:
        return self._mouse_wheel_has_moved.subscriber

    @property
    def keyboard_state_changed(self) -> OnEventSubscriber[set[int], None]:
        return self._keyboard_state_changed.subscriber

    def on_fixed_update(self, delta_time: float) -> None:
        self._fixed_update_started.invoke(delta_time)
        self._fixed_update_finished.invoke(delta_time)

    def on_update(self, delta_time: float) -> None:
        self._update_started.invoke(delta_time)
        self._update_finished.invoke(delta_time)

    def on_draw(self) -> None:
        self.clear()
        self._draw.invoke()

    def on_mouse_scroll(self, x: int, y: int, scroll_x: float, scroll_y: float) -> None:
        self._mouse_wheel_has_moved.invoke(scroll_y)

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> None:
        self._mouse_has_moved.invoke(Vector2(x, y))

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        is_left = button == arc.MOUSE_BUTTON_LEFT
        is_right = button == arc.MOUSE_BUTTON_RIGHT
        is_middle = button == arc.MOUSE_BUTTON_MIDDLE

        buttons = MouseButtons(is_left, is_right, is_middle)
        click = Click(Vector2(x, y), buttons)

        self._click_was_made.invoke(click)

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        self._pressed_keys.add(symbol)
        self._keyboard_state_changed.invoke(self._pressed_keys)

    def on_key_release(self, symbol: int, modifiers: int) -> None:
        self._pressed_keys.discard(symbol)
        self._keyboard_state_changed.invoke(self._pressed_keys)
