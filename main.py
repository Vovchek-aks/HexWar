from appearance.game_engine import make_game_engine
from core.game_session import GameSession
from mathematics.vector import Vector2Int

SCREEN_SHAPE = Vector2Int(1080, 720)
UPS = 60
CAPTION = "HexWar"


def main() -> None:
    session = GameSession.test_map(board_size=10)

    with make_game_engine(CAPTION, UPS, SCREEN_SHAPE, session) as engine:
        engine.run()


if __name__ == '__main__':
    main()
