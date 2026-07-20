from attrs import frozen, field

import core.protocols as proto
from core.moves.attack import Attack
from core.moves.capture import Capture
from core.moves.comnination import Combination
from core.moves.oreshnik_launch import OreshnikLaunch
from core.moves.pulling import PullingTermination, PullingInitiation
from core.moves.relocations import Relocation, Assault
from core.moves.creation import Creation
from core.moves.conversion import Conversion
from exceptions import NotSupportedMove
from mathematics.vector import Vector2Int
from observer import Event, OnEventSubscriber
from statuses import INVALID


@frozen
class MovesMaker(proto.MovesMaker):
    _session: proto.GameSession

    _move_was_made: Event[proto.ValidMove, None] = field(init=False, factory=Event)
    _board_move_was_made: Event[proto.ValidMove, None] = field(init=False, factory=Event)
    _cell_changed_owner: Event[Vector2Int, None] = field(init=False, factory=Event)
    _current_player_resources_flow_could_have_changed: Event[None] = field(init=False, factory=Event)
    _cells_to_annex_could_have_changed: Event[proto.Player, None] = field(init=False, factory=Event)

    @property
    def move_was_made(self) -> OnEventSubscriber[proto.ValidMove, None]:
        return self._move_was_made.subscriber

    @property
    def board_move_was_made(self) -> OnEventSubscriber[proto.ValidMove, None]:
        return self._board_move_was_made.subscriber

    @property
    def cell_changed_owner(self) -> OnEventSubscriber[Vector2Int, None]:
        return self._cell_changed_owner.subscriber

    @property
    def current_player_resources_flow_could_have_changed(self) -> OnEventSubscriber[None]:
        return self._current_player_resources_flow_could_have_changed.subscriber

    @property
    def cells_to_annex_could_have_changed(self) -> OnEventSubscriber[proto.Player, None]:
        return self._cells_to_annex_could_have_changed.subscriber

    def make(self, move: proto.ValidMove) -> None:
        assert move.move.validate(self._session) is not INVALID

        match move.move:  # move move
            case OreshnikLaunch():
                to_invoke = set[proto.Player]()
                for cell in move.move.get_target_cells(self._session):
                    if proto.PreventsAnnexations in cell.figure.FLAGS:
                        to_invoke.add(cell.owner)

                self._session.make(move)
                self._move_was_made.invoke(move)

                self._board_move_was_made.invoke(move)

                for player in to_invoke:
                    self._cells_to_annex_could_have_changed.invoke(player)

            case Assault(to_coord=to_coord, from_coord=from_coord):
                to_invoke = set[proto.Player]()
                if proto.PreventsAnnexations in self._session.board[to_coord].figure.FLAGS:
                    to_invoke.add(self._session.board[to_coord].owner)
                if proto.PreventsAnnexations in self._session.board[from_coord].figure.FLAGS:
                    to_invoke.add(self._session.board[from_coord].owner)

                self._session.make(move)
                self._move_was_made.invoke(move)

                self._cell_changed_owner.invoke(to_coord)

                self._board_move_was_made.invoke(move)

                for player in to_invoke:
                    self._cells_to_annex_could_have_changed.invoke(player)

            case Relocation(to_coord=to_coord):
                self._session.make(move)
                self._move_was_made.invoke(move)

                self._board_move_was_made.invoke(move)

                if proto.PreventsAnnexations in self._session.board[to_coord].figure.FLAGS:
                    self._cells_to_annex_could_have_changed.invoke(self._session.board[to_coord].owner)

            case Capture(to_coord=to_coord, from_coord=from_coord):
                to_invoke = set[proto.Player]()
                if proto.PreventsAnnexations in self._session.board[to_coord].figure.FLAGS:
                    to_invoke.add(self._session.board[to_coord].owner)
                    to_invoke.add(self._session.board[from_coord].owner)

                self._session.make(move)
                self._move_was_made.invoke(move)

                self._cell_changed_owner.invoke(to_coord)
                self._board_move_was_made.invoke(move)
                self._current_player_resources_flow_could_have_changed.invoke()

                for player in to_invoke:
                    self._cells_to_annex_could_have_changed.invoke(player)

            case Creation(to_coord=coord):
                self._session.make(move)
                self._move_was_made.invoke(move)

                self._board_move_was_made.invoke(move)
                self._current_player_resources_flow_could_have_changed.invoke()

                if proto.PreventsAnnexations in self._session.board[coord].figure.FLAGS:
                    self._cells_to_annex_could_have_changed.invoke(self._session.board[coord].owner)

            case Conversion(coord=coord, target=target):
                need_to_invoke = any([
                    proto.PreventsAnnexations in self._session.board[coord].figure.FLAGS,
                    proto.PreventsAnnexations in target.FLAGS
                ])

                self._session.make(move)
                self._move_was_made.invoke(move)

                self._board_move_was_made.invoke(move)
                self._current_player_resources_flow_could_have_changed.invoke()

                if need_to_invoke:
                    self._cells_to_annex_could_have_changed.invoke(self._session.board[coord].owner)

            case Combination(first_coord=coord, second_coord=second_coord, target=target):
                need_to_invoke = any([
                    proto.PreventsAnnexations in self._session.board[coord].figure.FLAGS,
                    proto.PreventsAnnexations in self._session.board[second_coord].figure.FLAGS,
                    proto.PreventsAnnexations in target.FLAGS
                ])

                self._session.make(move)
                self._move_was_made.invoke(move)

                self._board_move_was_made.invoke(move)
                self._current_player_resources_flow_could_have_changed.invoke()

                if need_to_invoke:
                    self._cells_to_annex_could_have_changed.invoke(self._session.board[coord].owner)

            case Attack(to_coord=coord):
                need_to_invoke = proto.PreventsAnnexations in self._session.board[coord].figure.FLAGS

                self._session.make(move)
                self._move_was_made.invoke(move)

                self._board_move_was_made.invoke(move)
                self._current_player_resources_flow_could_have_changed.invoke()

                if need_to_invoke:
                    self._cells_to_annex_could_have_changed.invoke(self._session.board[coord].owner)

            case PullingInitiation() | PullingTermination():
                self._session.make(move)
                self._move_was_made.invoke(move)

                self._board_move_was_made.invoke(move)

            case move:
                raise NotSupportedMove(move)
