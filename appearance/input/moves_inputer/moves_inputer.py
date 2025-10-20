from attrs import frozen

from appearance.input.clicks_catcher.layers.board_layer import BoardLayer
from mathematics.vector import Vector2Int


@frozen
class MovesInputer:
    @classmethod
    def make(cls, board_layer: BoardLayer) -> "MovesInputer":
        reader = cls()
        board_layer.cell_was_clicked.subscribe(reader._on_cell_was_clicked)
        return reader

    def _on_cell_was_clicked(self, coord: Vector2Int) -> None:
        print(f"Clicked board at {coord}")
