from abc import ABCMeta

from attrs import frozen

import core.protocols as proto


@frozen
class Resource(proto.Resource, metaclass=ABCMeta):
    amount: int = 0

    def _is_similar_types(self, other: "Resource") -> bool:
        return (isinstance(self, type(other)) or
                isinstance(other, type(self)))

    def __add__(self, other: "Resource") -> "Resource":
        assert self._is_similar_types(other)

        return type(self)(self.amount + other.amount)

    def __sub__(self, other: "Resource") -> "Resource":
        assert self._is_similar_types(other)

        return type(self)(self.amount - other.amount)


class Dollars(Resource):
    ...


class Oil(Resource):
    ...


class LightIndustryProducts(Resource):
    ...


class HeavyIndustryProducts(Resource):
    ...


def get_resources_types() -> list[type[Resource]]:
    return [
        Dollars,
        Oil,
        LightIndustryProducts,
        HeavyIndustryProducts,
    ]
