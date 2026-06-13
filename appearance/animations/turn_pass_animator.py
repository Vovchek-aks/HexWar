from attrs import frozen

from appearance.animations.basic import Animation, until_happen, sleep_gametime
from appearance.animations.to_target_orientation_camera_mover import ToTargetOrientationCameraMover
from appearance.game_engine.game_engine_arc.in_game_time import InGameTime
from appearance.graphics.camera.camera_orientation import CameraOrientation
from core.player.inputers.bot_player_inputer import BotPlayerInputer
from core.protocols import GameSession, Player, AnnexationMapUpdater
import appearance.protocols as proto
import core.figures.figure as fig

AFTER_TURN_WAIT_TIME = 0
ON_FULL_BOARD_WAIT_TIME = 1.5
FOR_MULTIBOT_MOVE_TIME = 1.5
FOR_GAME_MOVE_TIME = 1
MARGIN = 2


@frozen
class TurnPassAnimator:
    _camera: proto.Camera
    _to_target_camera_mover: ToTargetOrientationCameraMover
    _in_game_time: InGameTime
    _session: GameSession
    _hatching_map_updater: proto.AnnexationHatchingMapUpdater
    _annexation_map_updater: AnnexationMapUpdater

    @property
    def _is_annexations_display_in_progress(self) -> bool:
        return self._annexation_map_updater.is_active  # or self._hatching_map_updater.is_active

    def start_for_game(self, player: Player) -> Animation:
        yield
        if isinstance(player.inputer, BotPlayerInputer):
            return

        yield from sleep_gametime(FOR_GAME_MOVE_TIME, self._in_game_time)

        board = self._session.board
        cells = self._session.cells.with_owner(player)
        target = CameraOrientation.for_cells(cells, board, self._camera, margin=MARGIN)
        self._to_target_camera_mover.set_target(target, time=FOR_GAME_MOVE_TIME)
        yield
        yield from until_happen(self._to_target_camera_mover.target_has_been_reached)
        yield

    def end_for_game(self, player: Player) -> Animation:
        yield
        if isinstance(player.inputer, BotPlayerInputer):
            return

        while self._is_annexations_display_in_progress:
            yield

    def start_for_multibot(self, player: Player) -> Animation:
        while self._is_annexations_display_in_progress:
            yield

        yield from sleep_gametime(AFTER_TURN_WAIT_TIME, self._in_game_time)
        yield

        board = self._session.board
        target = CameraOrientation.for_board(board)
        self._to_target_camera_mover.set_target(target, time=FOR_MULTIBOT_MOVE_TIME)
        yield from until_happen(self._to_target_camera_mover.target_has_been_reached)

        yield from sleep_gametime(ON_FULL_BOARD_WAIT_TIME, self._in_game_time)
        yield

        cells = self._session.cells.with_owner(player)
        if self._session.cells.with_figure(fig.MissileSilo) & cells:
            neighbors = cells.at_outer_boundry(board).players()
            for neighbor in neighbors:
                cells += self._session.cells.with_owner(neighbor)

        if not cells:
            return

        target = CameraOrientation.for_cells(cells, board, self._camera, margin=MARGIN)
        if (ratio := self._camera.orientation.zoom / target.zoom) > 1:
            target.zoom_in(ratio)
        self._to_target_camera_mover.set_target(target, time=FOR_MULTIBOT_MOVE_TIME)
        yield
        yield from until_happen(self._to_target_camera_mover.target_has_been_reached)
        yield

        while self._is_annexations_display_in_progress:
            yield

    def end_for_multibot(self, _: Player) -> Animation:
        while self._is_annexations_display_in_progress:
            yield
