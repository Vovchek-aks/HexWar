from attrs import frozen

import core.protocols as proto
from core.resources import ResourcesGroup
from mathematics.vector import Vector2Int


@frozen
class TriesTakeResourcesElseDies(proto.TriesTakeResourcesElseDies):
    EXCLUDES = {}

    @classmethod
    def make(cls, *resources: proto.Resource) -> proto.TriesTakeResourcesElseDies:
        return cls(ResourcesGroup.make(*resources))

    _resources: proto.ResourcesGroup

    @property
    def resources(self) -> proto.ResourcesGroup:
        return self._resources

    def update(self, coord: Vector2Int, session: proto.GameSession) -> None:
        resources = session.master.current_player.resources
        if resources.can_take(self._resources):
            resources.take(self._resources)
            return
        session.figures.remove_at(coord)


@frozen
class AddsResourcesIndefinably(proto.AddsResourcesIndefinably):
    EXCLUDES = {}

    @classmethod
    def make(cls, *base_resources: proto.Resource) -> proto.AddsResourcesIndefinably:
        return cls(ResourcesGroup.make(*base_resources))

    _base_resources: proto.ResourcesGroup

    @property
    def base_resources(self) -> proto.ResourcesGroup:
        return self._base_resources

    def get_resources_with_buffs(self, coord: Vector2Int, session: proto.GameSession) -> proto.ResourcesGroup:
        player = session.board[coord].owner
        cells = session.cells.with_owner(player)
        cells &= session.cells.not_empty()
        cells = cells.with_flag(proto.BuffsResourceAdders)

        buff = 0
        for the_one_who_buffs in cells:
            flag = the_one_who_buffs.figure.FLAGS.get(proto.BuffsResourceAdders)
            buff += flag.get_buff(coord, session.board.coordinates_of(the_one_who_buffs), session)

        return self._base_resources * (1 + buff)

    def update(self, coord: Vector2Int, session: proto.GameSession) -> None:
        resource = self.get_resources_with_buffs(coord, session)
        session.master.current_player.resources.add(resource)


@frozen
class BuffsNeighborResourceAdders(proto.BuffsNeighborResourceAdders):
    EXCLUDES = {proto.ResourcesAdder}

    _ratio: float

    @property
    def ratio(self) -> float:
        return self._ratio

    def get_buff(self, resources_adder_coord: Vector2Int, coord: Vector2Int, session: proto.GameSession) -> float:
        board = session.board
        cell = board[coord]
        resource_adder = board[resources_adder_coord]
        assert cell.owner == resource_adder.owner

        if resource_adder not in board.get_neighbors(cell):
            return 0

        return self._ratio


def get_resource_flow(player: proto.Player, target: type[proto.Resource], session: proto.GameSession) -> int:
    cells = session.cells.with_owner(player)
    cells &= session.cells.not_empty()
    adders = cells.with_flag(proto.ResourcesAdder)
    takers = cells.with_flag(proto.TriesTakeResourcesElseDies)

    total = 0
    for adder in adders:
        flag = adder.figure.FLAGS.get(proto.ResourcesAdder)
        resources = flag.get_resources_with_buffs(session.board.coordinates_of(adder), session)
        total += resources.get(target).amount
    for taker in takers:
        flag = taker.figure.FLAGS.get(proto.TriesTakeResourcesElseDies)
        resources = flag.resources
        total -= resources.get(target).amount

    return total
