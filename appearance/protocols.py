from abc import ABC, abstractmethod, ABCMeta
from types import TracebackType
from typing import Callable, Iterator

import arcade as arc

from color import Color
from font import Font
from mathematics.angle import Angle
from mathematics.rectangle import Rectangle
from mathematics.vector import Vector2, Vector2Int
from observer import OnEventSubscriber
from statuses import Status
from appearance.graphics.sprites import Sprite
import core.protocols as proto


class Camera(ABC):
    @property
    @abstractmethod
    def orientation(self) -> "ReadonlyCameraOrientation":
        ...

    @abstractmethod
    def world_to_screen(self, point: Vector2) -> Vector2:
        ...

    @abstractmethod
    def screen_to_world(self, point: Vector2) -> Vector2:
        ...


class CameraOrientation(ABC):
    @property
    @abstractmethod
    def has_changed(self) -> OnEventSubscriber[None]:
        ...

    @property
    @abstractmethod
    def position(self) -> Vector2:
        ...

    @property
    @abstractmethod
    def rotation(self) -> Angle:
        ...

    @property
    @abstractmethod
    def zoom(self) -> float:
        ...

    @property
    @abstractmethod
    def tuple(self) -> tuple[Vector2, Angle, float]:
        ...

    @abstractmethod
    def set_starter(self) -> None:
        ...

    @abstractmethod
    def update(self) -> None:
        ...

    @abstractmethod
    def move(self, delta: Vector2) -> "CameraOrientation":
        ...

    @abstractmethod
    def rotate(self, angle: Angle) -> "CameraOrientation":
        ...

    @abstractmethod
    def zoom_in(self, ratio: float) -> "CameraOrientation":
        ...


class ReadonlyCameraOrientation(ABC):
    @property
    @abstractmethod
    def has_changed(self) -> OnEventSubscriber[None]:
        ...

    @property
    @abstractmethod
    def position(self) -> Vector2:
        ...

    @property
    @abstractmethod
    def rotation(self) -> Angle:
        ...

    @property
    @abstractmethod
    def zoom(self) -> float:
        ...

    @property
    @abstractmethod
    def tuple(self) -> tuple[Vector2, Angle, float]:
        ...

    @abstractmethod
    def mutable_copy(self) -> CameraOrientation:
        ...


class Draw(ABC):
    @abstractmethod
    def board(self) -> None:
        ...

    @abstractmethod
    def background(self) -> None:
        ...

    @abstractmethod
    def under_cursor_cell(self, cell_coord: Vector2Int) -> None:
        ...

    @abstractmethod
    def selected_cell(self, cell_coord: Vector2Int) -> None:
        ...

    @abstractmethod
    def board_sprites(self) -> None:
        ...


class OnBoardSpritesDrawer(ABC):
    @abstractmethod
    def add_sprite(self, sprite: Sprite, coord: Vector2Int, *, scale_ratio: float = 1) -> int:
        ...

    @abstractmethod
    def draw(self) -> None:
        ...

    @abstractmethod
    def get_sprite(self, index: int) -> arc.Sprite:
        ...

    @abstractmethod
    def remove_sprite(self, index: int) -> None:
        ...


class FiguresDrawer(ABC):
    @property
    @abstractmethod
    def figures_sprites(self) -> "FiguresSprites":
        ...

    @abstractmethod
    def get_figure_index(self, cell_coord) -> int:
        ...

    @abstractmethod
    def update_cell(self, cell_coord: Vector2Int) -> None:
        ...


class FiguresSprites(ABC):
    @abstractmethod
    def get(self, figure: type[proto.Figure]) -> Sprite:
        ...


class BordDrawer(ABC):
    @abstractmethod
    def draw_board(self) -> None:
        ...

    @abstractmethod
    def draw_highlighted(self, cell_coord: Vector2Int, highlight_ratio: float) -> None:
        ...


class BackgroundDrawer(ABC):
    def draw_background(self) -> None:
        ...


class CameraAssistant(ABC):
    @abstractmethod
    def __enter__(self) -> "CameraAssistant":
        ...

    @abstractmethod
    def __exit__(self,
                 exc_type: type[BaseException],
                 exc_val: BaseException,
                 exc_tb: TracebackType) -> bool | None:
        ...


class MovesAnimator(ABC):
    def get_animation(self, move: proto.Move) -> Iterator[None] | Status:
        ...


class UiDrawer(ABC):
    @abstractmethod
    def draw_text(self, text_data: "TextData", rectangle: Rectangle) -> None:
        ...

    @abstractmethod
    def draw_image(self, sprite: Sprite, position: Vector2) -> None:
        ...


class UnderCursorCellGetter(ABC):
    @abstractmethod
    def get_coord(self, mouse_position: Vector2) -> Vector2Int | Status:
        ...


class CellSelector(ABC):
    @classmethod
    @abstractmethod
    def make(cls,
             actions_reader: "InputActionsReader",
             moves_maker: proto.MovesMaker,
             master: proto.Master) -> "CellSelector":
        ...

    @property
    @abstractmethod
    def cell_was_selected(self) -> OnEventSubscriber[Vector2Int, None]:
        ...

    @property
    @abstractmethod
    def cell_was_unselected(self) -> OnEventSubscriber[None, None]:
        ...

    @abstractmethod
    def get_coord(self) -> Vector2Int | Status:
        ...


class MouseButtons(ABC):
    @property
    @abstractmethod
    def is_left(self) -> bool:
        ...

    @property
    @abstractmethod
    def is_right(self) -> bool:
        ...

    @property
    @abstractmethod
    def is_middle(self) -> bool:
        ...


class Click(ABC):
    @property
    @abstractmethod
    def screen_position(self) -> Vector2:
        ...

    @property
    @abstractmethod
    def buttons(self) -> MouseButtons:
        ...


class MouseMovementObserver(ABC):
    @property
    @abstractmethod
    def mouse_was_moved(self) -> OnEventSubscriber[Vector2, None]:
        ...

    @property
    @abstractmethod
    def mouse_position(self) -> Vector2:
        ...

    @abstractmethod
    def update(self, mouse_position: Vector2) -> None:
        ...


class DrawableLayer(ABC):
    @abstractmethod
    def draw(self, mouse_position: Vector2) -> None:
        ...


class ClicksCatchingLayer(ABC):
    @property
    @abstractmethod
    def was_clicked(self) -> OnEventSubscriber[Click, None]:
        ...

    @abstractmethod
    def can_catch(self, click: Click) -> bool:
        ...

    @abstractmethod
    def catch(self, click: Click) -> None:
        ...


class Layer(DrawableLayer, ClicksCatchingLayer):
    @property
    @abstractmethod
    def drawable_layer(self) -> DrawableLayer:
        ...

    @property
    @abstractmethod
    def clicks_catching_layer(self) -> ClicksCatchingLayer:
        ...

    @property
    @abstractmethod
    def is_active(self) -> bool:
        ...

    @abstractmethod
    def set_activity(self, activity: bool) -> None:
        ...

    @abstractmethod
    def draw(self, mouse_position: Vector2) -> None:
        ...

    @abstractmethod
    def can_catch(self, click: Click) -> bool:
        ...

    @abstractmethod
    def catch(self, click: Click) -> None:
        ...


class LayerHolder(ABC):
    @property
    @abstractmethod
    def layer(self) -> Layer:
        ...


class BoardLayer(ClicksCatchingLayer, metaclass=ABCMeta):
    @property
    @abstractmethod
    def cell_was_clicked(self) -> OnEventSubscriber[Vector2Int, MouseButtons, None]:
        ...


class WholeScreenLayer(ClicksCatchingLayer, metaclass=ABCMeta):
    ...


class LayersContainerLayer(ClicksCatchingLayer, metaclass=ABCMeta):
    ...


class MovesInputer(ABC):
    @property
    @abstractmethod
    def move_was_raed(self) -> OnEventSubscriber[proto.ValidMove, None]:
        ...


class InputAction(ABC):
    ...


class InputActionsReader(ABC):
    @property
    @abstractmethod
    def action_was_read(self) -> OnEventSubscriber[InputAction, bool, None]:
        ...

    @property
    @abstractmethod
    def action_was_removed(self) -> OnEventSubscriber[InputAction, bool, None]:
        ...

    @property
    @abstractmethod
    def actions(self) -> list[InputAction]:
        ...

    @abstractmethod
    def clear(self) -> None:
        ...

    @abstractmethod
    def pop(self) -> None:
        ...


class ElementUi(LayerHolder, metaclass=ABCMeta):
    @property
    @abstractmethod
    def rectangle(self) -> Rectangle:
        ...

    @abstractmethod
    def set_rectangle(self, rectangle: Rectangle) -> None:
        ...


class TextData(ABC):
    @property
    @abstractmethod
    def text(self) -> str:
        ...

    @property
    @abstractmethod
    def color(self) -> Color:
        ...

    @property
    @abstractmethod
    def font(self) -> Font:
        ...

    @property
    @abstractmethod
    def tuple(self) -> tuple[str, Font, Color]:
        ...

    @property
    @abstractmethod
    def shape(self) -> Vector2:
        ...

    @abstractmethod
    def with_text(self, text: str) -> "TextData":
        ...

    @abstractmethod
    def with_color(self, color: Color) -> "TextData":
        ...


class Scene(ABC):
    @abstractmethod
    def next(self) -> "Scene | Status":
        ...

    @abstractmethod
    def update(self) -> None:
        ...

    @abstractmethod
    def draw(self) -> None:
        ...

    @abstractmethod
    def __enter__(self) -> "Scene":
        ...

    @abstractmethod
    def __exit__(self,
                 exc_type: type[BaseException],
                 exc_val: BaseException,
                 exc_tb: TracebackType) -> bool | None:
        ...


class SceneSwitcher(ABC):
    @property
    @abstractmethod
    def scene(self) -> Scene:
        ...

    @abstractmethod
    def update(self, on_game_exit: Callable[[], None]) -> None:
        ...


class InputState(ABC):
    @property
    @abstractmethod
    def dt(self) -> float:
        ...

    @property
    @abstractmethod
    def mouse_position(self) -> Vector2:
        ...

    @property
    @abstractmethod
    def pressed_keys(self) -> set[int]:
        ...

    @property
    @abstractmethod
    def last_frame_clicks(self) -> list[Click]:
        ...

    @property
    @abstractmethod
    def last_frame_mouse_wheel_delta(self) -> float:
        ...


class Updater(ABC):
    @abstractmethod
    def update(self, input_state: InputState) -> None:
        ...


class FrameDrawer(ABC):
    @abstractmethod
    def draw_frame(self, mouse_position: Vector2) -> None:
        ...
