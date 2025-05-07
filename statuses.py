from attrs import frozen


@frozen
class Status:
    ...


INVALID = Status()
MISSING = Status()
