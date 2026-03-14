from attrs import frozen

import core.protocols as proto
from core.resources import Dollars
from mathematics.vector import Vector2Int


@frozen
class TriesTakeResourcesElseDies(proto.TriesTakeResourcesElseDies):
    EXCLUDES = {}

    _resource: proto.Resource

    @property
    def resource(self) -> proto.Resource:
        return self._resource

    def update(self, coord: Vector2Int, session: proto.GameSession) -> None:
        resources = session.master.current_player.resources
        if resources.can_take(self._resource):
            resources.take(self._resource)
            return
        session.figures.remove_at(coord)


@frozen
class AddsResourcesIndefinably(proto.AddsResourcesIndefinably):
    EXCLUDES = {}

    _base_resource: proto.Resource

    @property
    def base_resource(self) -> proto.Resource:
        return self._base_resource

    def get_resource_with_buffs(self, coord: Vector2Int, session: proto.GameSession) -> proto.Resource:
        player = session.board[coord].owner
        cells = session.cells.with_owner(player)
        cells &= session.cells.not_empty()
        cells = cells.with_flag(proto.BuffsResourceAdders)

        buff = 0
        for the_one_who_buffs in cells:
            flag = the_one_who_buffs.figure.FLAGS.get(proto.BuffsResourceAdders)
            buff += flag.get_buff(coord, session.board.coordinates_of(the_one_who_buffs), session)

        return self._base_resource * (1 + buff)

    def update(self, coord: Vector2Int, session: proto.GameSession) -> None:
        resource = self.get_resource_with_buffs(coord, session)
        session.master.current_player.resources.add(resource)


@frozen
class BuffsNeighborResourceAdders(proto.BuffsNeighborResourceAdders):
    EXCLUDES = {proto.ResourceAdder}

    _ratio: float

    @property
    def ratio(self) -> float:
        return self._ratio

    def get_buff(self,
                 resource_adder_coord: Vector2Int,
                 coord: Vector2Int,
                 session: proto.GameSession) -> float:
        board = session.board
        cell = board[coord]
        resource_adder = board[resource_adder_coord]
        assert cell.owner == resource_adder.owner

        if resource_adder not in board.get_neighbors(cell):
            return 0

        return self._ratio


def get_resource_flow(player: proto.Player, resource: type[proto.Resource], session: proto.GameSession) -> int:
    assert issubclass(resource, Dollars)  # temp

    cells = session.cells.with_owner(player)
    cells &= session.cells.not_empty()
    adders = cells.with_flag(proto.ResourceAdder)
    takers = cells.with_flag(proto.TriesTakeResourcesElseDies)

    total = 0
    for adder in adders:
        flag = adder.figure.FLAGS.get(proto.ResourceAdder)
        resource = flag.get_resource_with_buffs(session.board.coordinates_of(adder), session)
        if isinstance(resource, Dollars):
            total += resource.amount
    for taker in takers:
        flag = taker.figure.FLAGS.get(proto.TriesTakeResourcesElseDies)
        resource = flag.resource
        if isinstance(resource, Dollars):
            total -= resource.amount

    return total
