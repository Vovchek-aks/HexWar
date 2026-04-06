from typing import Iterator

from attrs import frozen, field

from core.resources import get_resources_types, Resource
import core.protocols as proto


@frozen(order=False)
class ResourcesGroup(proto.ResourcesGroup):
    @classmethod
    def make(cls, *some_resources: Resource) -> "ResourcesGroup":
        types = list(map(type, some_resources))
        assert len(types) == len(set(types))

        resources = list[Resource]()
        for resource in get_resources_types():
            if resource not in types:
                resources.append(resource())
                continue

            index = types.index(resource)
            resources.append(some_resources[index])

        return cls(tuple(resources))

    _resources: tuple[Resource, ...] = field(factory=lambda: tuple(
        resource() for resource in get_resources_types()
    ))

    @_resources.validator
    def _validate_resources(self, _, resources: list[Resource]) -> None:
        assert list(map(type, resources)) == get_resources_types()

    @property
    def not_zero(self) -> list[Resource]:
        return [resource for resource in self if resource]

    def get(self, target: type[Resource]) -> Resource:
        for resource in self._resources:
            if isinstance(resource, target):
                return resource

        assert False

    def __add__(self, other: "ResourcesGroup") -> "ResourcesGroup":
        return ResourcesGroup(tuple(our + others for our, others in zip(self, other)))

    def __sub__(self, other: "ResourcesGroup") -> "ResourcesGroup":
        return ResourcesGroup(tuple(our - others for our, others in zip(self, other)))

    def __mul__(self, multiplier: float) -> "ResourcesGroup":
        return ResourcesGroup(tuple(our * multiplier for our in self))

    def __ge__(self, other: "ResourcesGroup") -> bool:
        return all(our >= others for our, others in zip(self, other))

    def __bool__(self) -> bool:
        return any(self._resources)

    def __iter__(self) -> Iterator[Resource]:
        return iter(self._resources)
