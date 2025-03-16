from enum import Enum, auto


class Flag(Enum):
    STATIC = auto()
    MOVABLE = auto()
    CREATABLE = auto()
    UPGRADABLE = auto()
