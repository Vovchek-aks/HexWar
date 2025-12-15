from appearance.game_engine import make_game_engine
from core.game_session import test_map
from mathematics.vector import Vector2Int

SCREEN_SHAPE = Vector2Int(1280, 720)
UPS = 60
CAPTION = "HexWar"
IS_BOTS_ONLY = False


def main() -> None:
    session = test_map(board_size=10, initial_town_ratio=.2)
    engine, user_inputer = make_game_engine(CAPTION, UPS, SCREEN_SHAPE, session)
    if not IS_BOTS_ONLY:
        session.master.current_player.change_inputer(user_inputer)

    with engine:
        engine.run()


if __name__ == '__main__':
    main()
