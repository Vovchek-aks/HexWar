from appearance.game_engine import GameEngine
from core.game_session import GameSession
from mathematics.vector import Vector2Int

SCREEN_SHAPE = Vector2Int(1080, 720)
UPS = 60
CAPTION = "HexWar"


def main() -> None:
    session = GameSession.test_map(board_size=10)

    with GameEngine.start(CAPTION, UPS, SCREEN_SHAPE, session) as engine:
        while not engine.need_to_stop():
            engine.update()


if __name__ == '__main__':
    main()
