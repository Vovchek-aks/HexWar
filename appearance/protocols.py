from abc import ABC, abstractmethod, ABCMeta

from color import Color
from font import Font
from mathematics.angle import Angle
from mathematics.vector import Vector2, Vector2Int
from mathematics.hex_geometry import Neighbor
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
    def figures(self) -> None:
        ...


class FiguresDrawer(ABC):
    @abstractmethod
    def draw_figures(self) -> None:
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
    def draw_background(self) -> None:
        ...

    @abstractmethod
    def draw_highlighted(self, cell_coord: Vector2Int, highlight_ratio: float) -> None:
        ...

    @abstractmethod
    def draw_edge(self, cell_coord: Vector2Int, neighbor: Neighbor) -> None:
        ...

    @abstractmethod
    def draw_edges(self, cell_coord: Vector2Int) -> None:
        ...

    @abstractmethod
    def draw_hex_background(self, cell_coord: Vector2Int) -> None:
        ...


class UiDrawer(ABC):
    @abstractmethod
    def draw_text(self, text_data: "TextData") -> None:
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
    def make(cls, actions_reader: "InputActionsReader", moves_maker: proto.MovesMaker) -> "CellSelector":
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


class Click(ABC):
    @property
    @abstractmethod
    def screen_position(self) -> Vector2:
        ...

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


class DrawableLayer(ABC):
    @abstractmethod
    def draw(self, mouse_position: Vector2) -> None:
        ...


class ClicksCatchingLayer(ABC):
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

    @abstractmethod
    def draw(self, mouse_position: Vector2) -> None:
        ...

    @abstractmethod
    def can_catch(self, click: Click) -> bool:
        ...

    @abstractmethod
    def catch(self, click: Click) -> None:
        ...


class BoardLayer(ClicksCatchingLayer, metaclass=ABCMeta):
    @property
    @abstractmethod
    def cell_was_clicked_left(self) -> OnEventSubscriber[Vector2Int, None]:
        ...

    @property
    @abstractmethod
    def cell_was_clicked_right(self) -> OnEventSubscriber[Vector2Int, None]:
        ...

    @property
    @abstractmethod
    def cell_was_clicked_middle(self) -> OnEventSubscriber[Vector2Int, None]:
        ...


class WholeScreenLayer(ClicksCatchingLayer, metaclass=ABCMeta):
    @property
    @abstractmethod
    def click_happened(self) -> OnEventSubscriber[Click, None]:
        ...


class LayersContainerLayer(ClicksCatchingLayer, metaclass=ABCMeta):
    ...


class MovesInputer(ABC):
    @classmethod
    @abstractmethod
    def make(cls, reader: "InputActionsReader", board: proto.Board, cell_selector: CellSelector) -> "MovesInputer":
        ...

    @property
    @abstractmethod
    def move_was_raed(self) -> OnEventSubscriber[proto.ValidMove, None]:
        ...


class InputAction(ABC):
    ...


class InputActionsReader(ABC):
    @classmethod
    @abstractmethod
    def make(cls, board_layer: BoardLayer, null_layer: WholeScreenLayer) -> "InputActionsReader":
        ...

    @property
    @abstractmethod
    def action_was_raed(self) -> OnEventSubscriber[InputAction, None]:
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


class TextData(ABC):
    @property
    @abstractmethod
    def position(self) -> Vector2:
        ...

    @property
    @abstractmethod
    def tuple(self) -> tuple[str, Font, Color, Vector2]:
        ...
