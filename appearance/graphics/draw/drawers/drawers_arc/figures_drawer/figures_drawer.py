from attrs import frozen, field

import appearance.protocols as proto
from core.protocols import Board
from mathematics.vector import Vector2Int
import core.figures.figure as fig


@frozen
class FiguresDrawer(proto.FiguresDrawer):
    @classmethod
    def make(cls,
             board: Board,
             figures_sprites: proto.FiguresSprites,
             on_board_sprites_drawer: proto.OnBoardSpritesDrawer) -> "FiguresDrawer":
        self = cls(board, figures_sprites, on_board_sprites_drawer)
        for cell_coord in self._board:
            self._add_figure_sprite(cell_coord)
        return self

    _board: Board
    _figures_sprites: proto.FiguresSprites
    _on_board_sprites_drawer: proto.OnBoardSpritesDrawer

    _figures: dict[Vector2Int, int] = field(init=False, factory=dict)

    @property
    def figures_sprites(self) -> proto.FiguresSprites:
        return self._figures_sprites

    def get_figure_index(self, cell_coord) -> int:
        assert cell_coord in self._figures

        return self._figures[cell_coord]

    def update_cell(self, cell_coord: Vector2Int) -> None:
        if cell_coord in self._figures:
            self._on_board_sprites_drawer.remove_sprite(self._figures.pop(cell_coord))

        self._add_figure_sprite(cell_coord)

    def _add_figure_sprite(self, cell_coord: Vector2Int) -> None:
        assert cell_coord not in self._figures

        figure = self._board[cell_coord].figure
        if isinstance(figure, fig.Land | fig.Water):
            return

        sprite = self._figures_sprites.get(type(figure))
        self._figures[cell_coord] = self._on_board_sprites_drawer.add_sprite(sprite, cell_coord)
