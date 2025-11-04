from core.protocols import Move


class NotImplementedMove(Exception):
    def __init__(self, move: Move) -> None:
        super().__init__(f"{type(move)}")


class NotSupportedMove(Exception):
    def __init__(self, move: Move) -> None:
        super().__init__(f"{type(move)}")
