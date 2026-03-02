from attrs import define, field

import core.protocols as proto
from core.figures import figure as fig
from statuses import MISSING, Status


@define(hash=True, eq=True, repr=False)
class Cell(proto.Cell):
    _owner: proto.Player | Status = field(hash=False, eq=False)
    _figure: proto.Figure = field(hash=False, eq=False)
    _id: int = field(init=False)

    def __attrs_post_init__(self) -> None:
        self._id = id(self)
        if proto.DontHaveOwner in self.figure.FLAGS:
            self._owner = MISSING

    @property
    def owner(self) -> proto.Player | Status:
        return self._owner

    @property
    def figure(self) -> proto.Figure:
        return self._figure

    @property
    def is_empty(self) -> bool:
        return proto.Empty in self.figure.FLAGS

    def hardness(self, board: proto.Board) -> int:
        assert board.has(self)

        return max(cell.figure.hardness(board.coordinates_of(cell), board)
                   for cell in board.get_neighbors(self, include_cell=True).with_owner(self.owner))

    def strength(self, board: proto.Board, *, strict: bool = True) -> int:
        assert board.has(self)

        if (movable := self.figure.FLAGS.get(proto.Movable)) is MISSING and not strict:
            return 0

        assert movable is not MISSING

        coord = board.coordinates_of(self)
        return movable.strength(coord, board)

    def pop(self) -> proto.Figure:
        assert not self.is_empty

        figure = self.figure
        self._figure = fig.Land() if figure.is_on_land() else fig.Water()
        return figure

    def insert(self, figure: proto.Figure) -> None:
        assert self.is_empty
        assert self.figure.is_on_land() == figure.is_on_land()

        self._figure = figure

    def change_owner(self, player: proto.Player) -> None:
        assert self._owner != player
        self._owner = player

    def take_from(self, other: proto.Cell) -> None:
        assert self.is_empty
        assert self.figure.is_on_land() == other.figure.is_on_land()

        if self.owner != other.owner:
            self.change_owner(other.owner)
        self._figure = other.pop()

    def turn_into_water(self) -> None:
        assert self.is_empty

        self._figure = fig.Water()
        self._owner = MISSING

    def turn_into_land(self, owner: proto.Player) -> None:
        assert self.is_empty

        self._figure = fig.Land()
        self._owner = owner

    def __str__(self) -> str:
        if self.owner is not MISSING:
            return f"{type(self).__name__}(figure: {type(self.figure).__name__}, owner: {self.owner.data.name})"

        return f"{type(self).__name__}(figure: {type(self.figure).__name__})"

    def __repr__(self) -> str:
        return str(self)
