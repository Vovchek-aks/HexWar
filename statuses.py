from attrs import frozen


@frozen(eq=False, hash=True)
class Status:
    def __eq__(self, other: 'Status') -> bool:
        return self is other


INVALID = Status()
MISSING = Status()
CAN_BECOME_CORRECT = Status()
