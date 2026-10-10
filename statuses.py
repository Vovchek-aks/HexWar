from attrs import frozen


@frozen(hash=True)
class Status:
    _name: str
    _bool: bool = False

    def __bool__(self) -> bool:
        return self._bool


INVALID = Status("INVALID")
MISSING = Status("MISSING")
CAN_BECOME_CORRECT = Status("CAN_BECOME_CORRECT")
ABORT_NEEDED = Status("ABORT_NEEDED")
IN_PROGRESS = Status("IN_PROGRESS")
DEFAULT = Status("DEFAULT")
