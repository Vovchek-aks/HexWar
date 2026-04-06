from abc import ABCMeta
from typing import Iterator

from attrs import frozen

import core.protocols as proto
from core.resources import ResourcesGroup
from mathematics.vector import Vector2Int
from statuses import Status, MISSING


@frozen
class TriesTakeResourcesElseDies(proto.TriesTakeResourcesElseDies):
    EXCLUDES = {}

    @classmethod
    def make(cls, *resources: proto.Resource) -> proto.TriesTakeResourcesElseDies:
        return cls(ResourcesGroup.make(*resources))

    _resources: proto.ResourcesGroup
    _priority: int = 100

    @property
    def priority(self) -> int:
        return self._priority

    @property
    def resources_to_take(self) -> proto.ResourcesGroup:
        return self._resources

    @property
    def changeable_resources(self) -> set[type[proto.Resource]]:
        return set(map(type[proto.Resource], self.resources_to_take.not_zero))

    def update(self, coord: Vector2Int, session: proto.GameSession) -> None:
        resources = session.master.current_player.resources
        if resources.can_take(self._resources):
            resources.take(self._resources)
            return
        session.figures.remove_at(coord)


class ResourcesAdder(proto.ResourcesAdder, metaclass=ABCMeta):
    @property
    def changeable_resources(self) -> set[type[proto.Resource]]:
        return set(map(type[proto.Resource], self.base_resources.not_zero))

    def get_resources_with_buffs(self, coord: Vector2Int, session: proto.GameSession) -> proto.ResourcesGroup:
        player = session.board[coord].owner
        cells = session.cells.with_owner(player)
        cells &= session.cells.not_empty()
        cells = cells.with_flag(proto.BuffsResourceAdders)

        buff = 0
        for the_one_who_buffs in cells:
            flag = the_one_who_buffs.figure.FLAGS.get(proto.BuffsResourceAdders)
            buff += flag.get_buff(coord, session.board.coordinates_of(the_one_who_buffs), session)

        return self.base_resources * (1 + buff)


@frozen
class AddsResourcesIndefinably(ResourcesAdder, proto.AddsResourcesIndefinably):
    EXCLUDES = {}

    @classmethod
    def make(cls, *base_resources: proto.Resource) -> proto.AddsResourcesIndefinably:
        return cls(ResourcesGroup.make(*base_resources))

    _base_resources: proto.ResourcesGroup
    _priority: int = 0

    @property
    def priority(self) -> int:
        return self._priority

    @property
    def base_resources(self) -> proto.ResourcesGroup:
        return self._base_resources

    def update(self, coord: Vector2Int, session: proto.GameSession) -> None:
        resources = self.get_resources_with_buffs(coord, session)
        session.master.current_player.resources.add(resources)


@frozen
class TransformsResourcesIndefinably(ResourcesAdder, proto.TransformsResourcesIndefinably, proto.ResourcesTaker):
    EXCLUDES = {}

    _input_resources: proto.ResourcesGroup
    _base_output_resources: proto.ResourcesGroup
    _priority: int = 10

    @property
    def priority(self) -> int:
        return self._priority

    @property
    def base_resources(self) -> proto.ResourcesGroup:
        return self._base_output_resources

    @property
    def input_resources(self) -> "ResourcesGroup":
        return self._input_resources

    @property
    def resources_to_take(self) -> "ResourcesGroup":
        return self.input_resources

    @property
    def changeable_resources(self) -> set[type[proto.Resource]]:
        return set(map(type[proto.Resource], (self.resources_to_take + self.base_resources).not_zero))

    def update(self, coord: Vector2Int, session: proto.GameSession) -> None:
        player_resources = session.master.current_player.resources
        if not player_resources.can_take(self._input_resources):
            return

        player_resources.take(self._input_resources)
        resources = self.get_resources_with_buffs(coord, session)
        player_resources.add(resources)


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
    for result in getting_resources_flow_process(player, target, session):
        if result is not MISSING:
            return result


def getting_resources_flow_process(player: proto.Player,
                                   target: type[proto.Resource],
                                   session: proto.GameSession) -> Iterator[Status | int]:
    cells = session.cells.with_owner(player)
    yield MISSING
    cells &= session.cells.not_empty()
    yield MISSING
    adders = cells.with_flag(proto.ResourcesAdder)
    yield MISSING
    takers = cells.with_flag(proto.ResourcesTaker)

    total = 0
    for adder in adders:
        yield MISSING
        flag = adder.figure.FLAGS.get(proto.ResourcesAdder)
        resources = flag.get_resources_with_buffs(session.board.coordinates_of(adder), session)
        total += resources.get(target).amount
    for taker in takers:
        yield MISSING
        flag = taker.figure.FLAGS.get(proto.ResourcesTaker)
        resources = flag.resources_to_take
        total -= resources.get(target).amount

    yield total
