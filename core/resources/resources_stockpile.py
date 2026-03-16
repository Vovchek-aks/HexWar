from attrs import define, field

from core.resources import Resource
import core.protocols as proto
from core.resources.resources_group import ResourcesGroup
from observer import Event, OnEventSubscriber


@define
class ResourcesStockpile(proto.ResourcesStockpile):
    _resources: ResourcesGroup = field(factory=ResourcesGroup)

    _has_changed: Event["ResourcesStockpile", None] = field(init=False, factory=Event)

    @property
    def has_changed(self) -> OnEventSubscriber["ResourcesStockpile", None]:
        return self._has_changed.subscriber

    def get(self, target: type[Resource]) -> Resource:
        return self._resources.get(target)

    def can_take(self, resources_to_take: ResourcesGroup) -> bool:
        print(self._resources)
        print(resources_to_take)
        return self._resources >= resources_to_take

    def add(self, additional_resources: ResourcesGroup) -> None:
        self._resources += additional_resources
        self._has_changed.invoke(self)

    def take(self, resources_to_take: ResourcesGroup) -> None:
        assert self.can_take(resources_to_take)

        self._resources -= resources_to_take
        self._has_changed.invoke(self)
