from attrs import frozen, field

from core.resources import get_resources_types, Resource
import core.protocols as proto
from observer import Event, OnEventSubscriber


@frozen
class ResourcesStockpile(proto.ResourcesStockpile):
    _has_changed: Event["ResourcesStockpile", None] = field(init=False, factory=Event)

    resources: list[Resource] = field(init=False, factory=lambda: [
        resource() for resource in get_resources_types()
    ])

    @property
    def has_changed(self) -> OnEventSubscriber["ResourcesStockpile", None]:
        return self._has_changed.subscriber

    def get(self, target: type[Resource]) -> Resource:
        for resource in self.resources:
            if isinstance(resource, target):
                return resource

        assert False

    def can_take(self, taken_resource: Resource) -> bool:
        resource = self.get(type(taken_resource))
        return resource.amount >= taken_resource.amount

    def add(self, additional_resource: Resource) -> None:
        resource = self.get(type(additional_resource))
        index = self.resources.index(resource)
        self.resources[index] += additional_resource
        self._has_changed.invoke(self)

    def take(self, taken_resource: Resource) -> None:
        assert self.can_take(taken_resource)

        resource = self.get(type(taken_resource))
        index = self.resources.index(resource)
        self.resources[index] -= taken_resource
        self._has_changed.invoke(self)
