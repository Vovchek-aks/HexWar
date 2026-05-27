import random
from typing import Callable

from attrs import frozen, define, field
import arcade as arc

from appearance.animations.basic import Animation, chain, call, cycle, no_animation, group, sleep_gametime
import appearance.protocols as proto
from appearance.audio.animation_sounds import AnimationSounds
from appearance.audio.sound.sounds_loader import SoundsLoader
from appearance.game_engine.game_engine_arc.in_game_time import InGameTime
from appearance.graphics.sprites import SpritesLoader
from core.moves.attack import Attack
from core.moves.capture import Capture
from core.moves.creation import Creation
from core.moves.oreshnik_launch import OreshnikLaunch
from core.moves.pulling import PullingInitiation
from core.moves.relocations import Assault, Relocation
from core.moves.conversion import Conversion
from core.protocols import Move, GameSession, Figure, Cells, Empty
from mathematics.angle import Angle
from mathematics.hex_geometry import get_world_position, DISTANCE_BETWEEN_CENTERS, get_direction
from mathematics.parabola import Parabola
from mathematics.vector import Vector2Int, Vector2
from statuses import Status, MISSING

ATTACK_EXPLOSION_DURATION = .6
ATTACK_KICKBACK_DURATION = .1
ATTACK_KICKBACK_RETURN_DURATION = .2
ATTACK_KICKBACK_DELTA_POSITION = DISTANCE_BETWEEN_CENTERS / 4
ATTACK_EXPLOSION_SCALE_RATIO = 1.5

RELOCATION_JUMP_DURATION = .2
RELOCATION_PULLING_LAG = .05
RELOCATION_JUMP_HEIGHT = DISTANCE_BETWEEN_CENTERS / 2

CAPTURE_DURATION = .5
CAPTURE_SHAKING_DURATION_RATIO = .8
CAPTURE_SHAKE_ANGLE = Angle(15)
CAPTURE_SCALE_RATIO = 1.5

CONVERSION_DURATION = .5

CREATION_DURATION = .5
CREATION_FIRST_JUMP_DURATION_RATIO = .6
CREATION_FIRST_JUMP_HEIGHT = DISTANCE_BETWEEN_CENTERS / 3
CREATION_SECOND_JUMP_HEIGHT = DISTANCE_BETWEEN_CENTERS / 8
CREATION_INITIAL_SCALE_RATIO = 0.2
CREATION_FINAL_SCALE_RATIO = 1.1

ORESHNIK_LAUNCH_FULL_FLIGHT_DURATION = 4
ORESHNIK_LAUNCH_VISIBLE_FLIGHT_DURATION_RATIO = .95
ORESHNIK_LAUNCH_FLIGHT_HEIGHT = DISTANCE_BETWEEN_CENTERS * 20
ORESHNIK_LAUNCH_ROCKET_SCALE = 1
ORESHNIK_LAUNCH_EXPLOSIONS_DURATION = .6
ORESHNIK_LAUNCH_EXPLOSIONS_MIN_LAG = 0
ORESHNIK_LAUNCH_EXPLOSIONS_MAX_LAG = .5
ORESHNIK_LAUNCH_EXPLOSIONS_MIN_SCALE_RATIO = 1
ORESHNIK_LAUNCH_EXPLOSIONS_MAX_SCALE_RATIO = 1.5


@frozen
class MovesAnimator(proto.MovesAnimator):
    @classmethod
    def make(cls,
             on_board_sprites_drawer: proto.OnBoardSpritesDrawer,
             figures_drawer: proto.FiguresDrawer,
             camera: proto.Camera,
             session: GameSession,
             in_game_time: InGameTime,
             *,
             speed_multiplier: float = 1,
             volume_multiplier: float = 1) -> "MovesAnimator":
        sprites_loader = SpritesLoader.from_meta()
        self = cls(
            speed_multiplier,
            in_game_time,
            SoundsLoader.from_meta().load_animation_sounds(volume_multiplier),
            figures_drawer,
            camera,
            session,
            on_board_sprites_drawer,
            sprites_loader.load_explosion(),
            sprites_loader.load_rocket(),
        )
        return self

    _speed_multiplier: float
    _in_game_time: InGameTime

    _sounds: AnimationSounds

    _figures_drawer: proto.FiguresDrawer
    _camera: proto.Camera
    _session: GameSession

    _on_board_sprites_drawer: proto.OnBoardSpritesDrawer
    _explosion: proto.Sprite
    _rocket: proto.Sprite

    def get_animation(self, move: Move) -> Animation | Status:
        if self._speed_multiplier == float('inf'):
            return MISSING

        match move:
            case PullingInitiation():
                return self._play_sound(self._sounds.pulling_initiation)
            case Attack(from_coord=coord, to_coord=target):
                return self._get_attack_animation(coord, target)
            case (Relocation(from_coord=from_coord, to_coord=to_coord) |
                  Assault(from_coord=from_coord, to_coord=to_coord)):
                animation = self._get_relocation_animation(from_coord, to_coord)
                if (pullable := move.pullable_cell(self._session)) is MISSING:
                    return animation
                pulling = self._get_relocation_animation(self._session.board.coordinates_of(pullable), from_coord)
                return group(chain(animation, cycle(no_animation)),
                             chain(self._sleep(RELOCATION_PULLING_LAG), pulling))
            case Capture(to_coord=coord):
                return self._get_capture_animation(coord)
            case Conversion(coord=coord, target=target):
                return self._get_conversion_animation(coord, target)
            case Creation(to_coord=coord, figure_type=figure):
                return self._get_creation_animation(coord, figure)
            case OreshnikLaunch(from_coord=coord, to_coord=target):
                return self._get_oreshnik_launch_animation(coord, target, move.get_target_cells(self._session))
            case _:
                return MISSING
        assert False

    def _get_attack_animation(self, coord: Vector2Int, target: Vector2Int) -> Animation:
        explosion = chain(group(self._play_sound(self._sounds.attack),
                                self._show_sprite(self._explosion, target, ATTACK_EXPLOSION_DURATION,
                                                  scale_ratio=ATTACK_EXPLOSION_SCALE_RATIO)),
                          cycle(no_animation))

        def _set_sprite_position(sprite: arc.Sprite, position: Vector2) -> None:
            sprite.position = position

        delta = -ATTACK_KICKBACK_DELTA_POSITION * get_direction(coord, target)
        artillery = self._get_sprite_at(coord)
        artillery_position = artillery.position
        kickback = chain(self._translate_sprite(artillery, lambda t: delta * t / ATTACK_KICKBACK_DURATION,
                                                ATTACK_KICKBACK_DURATION),
                         call(lambda: _set_sprite_position(artillery, artillery_position + delta)),
                         self._translate_sprite(artillery, lambda t: -delta * t / ATTACK_KICKBACK_RETURN_DURATION,
                                                ATTACK_KICKBACK_RETURN_DURATION),
                         call(lambda: self._figures_drawer.update_cell(coord)))
        return group(explosion, kickback)

    def _get_relocation_animation(self, from_coord: Vector2Int, to_coord: Vector2Int) -> Animation:
        figure = type(self._session.board[from_coord].figure)
        return chain(self._play_sound_fully(self._sounds.relocation_for(figure)),
                     self._jump(self._get_sprite_at(from_coord), from_coord, to_coord,
                                RELOCATION_JUMP_HEIGHT, RELOCATION_JUMP_DURATION))

    def _get_conversion_animation(self, coord: Vector2Int, figure_type: type[Figure]) -> Animation:
        sprite_index = self._figures_drawer.get_figure_index(coord)
        sprite = self._on_board_sprites_drawer.get_sprite(sprite_index)
        half_rotation_duration = CONVERSION_DURATION / 2
        half_circle = Angle(180)
        rotation_speed = half_circle.degrees / half_rotation_duration

        def other_half() -> Animation:
            figure = self._figures_drawer.figures_sprites.get(figure_type)
            target_index = self._on_board_sprites_drawer.add_sprite(figure, coord)
            target = self._on_board_sprites_drawer.get_sprite(target_index)
            target.angle += half_circle.degrees

            try:
                yield from self._rotate_sprite(target, lambda t: Angle(rotation_speed * t), half_rotation_duration)
            finally:
                self._on_board_sprites_drawer.remove_sprite(target_index)

        return chain(self._play_sound_fully(self._sounds.conversion),
                     self._rotate_sprite(sprite, lambda t: Angle(rotation_speed * t), half_rotation_duration),
                     self._hide_figure(coord),
                     other_half())

    def _get_capture_animation(self, coord: Vector2Int) -> Animation:
        if self._session.board[coord].is_empty:
            return no_animation()

        sprite = self._get_sprite_at(coord)
        initial_rotation = Angle(sprite.angle)
        shaking_duration = CAPTURE_DURATION * CAPTURE_SHAKING_DURATION_RATIO
        resizing_duration = (CAPTURE_DURATION - shaking_duration) / 2
        size_changing_speed = (CAPTURE_SCALE_RATIO - 1) * sprite.scale[0] / resizing_duration
        angle_changing_speed = CAPTURE_SHAKE_ANGLE * (1 / resizing_duration)
        shaking_angle_changing_speed = CAPTURE_SHAKE_ANGLE * (1 / shaking_duration)

        def set_rotation(rotation: Angle) -> None:
            sprite.angle = rotation.degrees

        return chain(group(self._resize_sprite(sprite, lambda t: size_changing_speed * t, resizing_duration),
                           self._rotate_sprite(sprite, lambda t: angle_changing_speed * t, resizing_duration)),
                     call(lambda: set_rotation(initial_rotation + CAPTURE_SHAKE_ANGLE)),
                     group(chain(self._play_sound_fully(self._sounds.capture), cycle(no_animation)),
                           chain(self._rotate_sprite(sprite, lambda t: shaking_angle_changing_speed * -t * 6,
                                                     shaking_duration / 3),
                                 call(lambda: set_rotation(initial_rotation + -CAPTURE_SHAKE_ANGLE)))),
                     group(chain(self._play_sound_fully(self._sounds.capture), cycle(no_animation)),
                           chain(self._rotate_sprite(sprite, lambda t: shaking_angle_changing_speed * t * 6,
                                                     shaking_duration / 3),
                                 call(lambda: set_rotation(initial_rotation + CAPTURE_SHAKE_ANGLE)))),
                     group(chain(self._play_sound_fully(self._sounds.capture), cycle(no_animation)),
                           chain(self._rotate_sprite(sprite, lambda t: shaking_angle_changing_speed * -t * 6,
                                                     shaking_duration / 3),
                                 call(lambda: set_rotation(initial_rotation + -CAPTURE_SHAKE_ANGLE)))),
                     group(self._resize_sprite(sprite, lambda t: -size_changing_speed * t, resizing_duration),
                           self._rotate_sprite(sprite, lambda t: angle_changing_speed * t, resizing_duration)),
                     call(lambda: self._figures_drawer.update_cell(coord)))

    def _get_creation_animation(self, coord: Vector2Int, figure_type: type[Figure]) -> Animation:
        # cost = figure_type.FLAGS.get(Creatable).cost.amount
        # duration = CREATION_DURATION_RATIO * (cost / 100_000)**.5
        duration = CREATION_DURATION

        figure = self._figures_drawer.figures_sprites.get(figure_type)
        sprite_index = self._on_board_sprites_drawer.add_sprite(figure, coord, scale_ratio=CREATION_INITIAL_SCALE_RATIO)
        sprite = self._on_board_sprites_drawer.get_sprite(sprite_index)

        first_jump_duration = duration * CREATION_FIRST_JUMP_DURATION_RATIO
        second_jump_duration = duration - first_jump_duration

        first_resizing_speed = (sprite.scale[0] *
                                (CREATION_FINAL_SCALE_RATIO / CREATION_INITIAL_SCALE_RATIO - 1))
        second_resizing_speed = (sprite.scale[0] *
                                 (CREATION_FINAL_SCALE_RATIO / CREATION_INITIAL_SCALE_RATIO) *
                                 (1 / CREATION_FINAL_SCALE_RATIO - 1) /
                                 second_jump_duration)

        try:
            yield from chain(group(self._jump(sprite, coord, coord, CREATION_FIRST_JUMP_HEIGHT, first_jump_duration),
                                   self._resize_sprite(sprite,
                                                       lambda t: first_resizing_speed * (t / first_jump_duration) ** 2,
                                                       first_jump_duration)),
                             group(self._play_sound(self._sounds.creation_landing),
                                   self._jump(sprite, coord, coord, CREATION_SECOND_JUMP_HEIGHT, second_jump_duration),
                                   self._resize_sprite(sprite, lambda t: second_resizing_speed * t,
                                                       second_jump_duration)))
        finally:
            self._on_board_sprites_drawer.discard_sprite(sprite_index)

    def _get_oreshnik_launch_animation(self, coord: Vector2Int, target: Vector2Int, targets: Cells) -> Animation:
        explosions = group(*[chain(self._sleep(random.uniform(ORESHNIK_LAUNCH_EXPLOSIONS_MIN_LAG,
                                                              ORESHNIK_LAUNCH_EXPLOSIONS_MAX_LAG)),
                                   group(self._play_sound(self._sounds.explosion),
                                         self._show_sprite(self._explosion,
                                                           self._session.board.coordinates_of(explosion_cell),
                                                           ORESHNIK_LAUNCH_EXPLOSIONS_DURATION,
                                                           scale_ratio=random.uniform(
                                                               ORESHNIK_LAUNCH_EXPLOSIONS_MIN_SCALE_RATIO,
                                                               ORESHNIK_LAUNCH_EXPLOSIONS_MAX_SCALE_RATIO))),
                                   (self._hide_figure(self._session.board.coordinates_of(explosion_cell))
                                    if Empty not in explosion_cell.figure.FLAGS else
                                    no_animation()),
                                   cycle(no_animation))
                             for explosion_cell in targets],
                           self._sleep(ORESHNIK_LAUNCH_EXPLOSIONS_DURATION + ORESHNIK_LAUNCH_EXPLOSIONS_MAX_LAG))

        rocket_index = self._on_board_sprites_drawer.add_sprite(self._rocket, coord,
                                                                scale_ratio=ORESHNIK_LAUNCH_ROCKET_SCALE)
        rocket = self._on_board_sprites_drawer.get_sprite(rocket_index)

        jump_arguments = (coord,
                          target,
                          ORESHNIK_LAUNCH_FLIGHT_HEIGHT,
                          ORESHNIK_LAUNCH_FULL_FLIGHT_DURATION)
        get_jump_delta_position = self._get_jump_delta_position_getter(*jump_arguments)

        def get_rocket_delta_angle(t: float) -> Angle:
            if t == 0:
                return Angle(0)

            dt = 0.01
            if t <= dt:
                return Angle(0)

            delta_position = ((get_jump_delta_position(t) - get_jump_delta_position(t - dt)) / dt)
            if delta_position.length() == 0:
                return Angle(0)

            direction = delta_position.with_x(-delta_position.y).with_y(delta_position.x).normalize()
            up = self._camera.orientation.rotation.inverse.apply(-Vector2.right()).normalize()
            return -Angle(up.angle_to(direction))

        flight = chain(group(chain(self._play_sound(self._sounds.oreshnik_flight), cycle(no_animation)),
                             self._jump(rocket, *jump_arguments),
                             self._rotate_sprite(rocket, get_rocket_delta_angle, ORESHNIK_LAUNCH_FULL_FLIGHT_DURATION),
                             self._sleep(ORESHNIK_LAUNCH_FULL_FLIGHT_DURATION *
                                         ORESHNIK_LAUNCH_VISIBLE_FLIGHT_DURATION_RATIO)),
                       call(lambda: self._on_board_sprites_drawer.discard_sprite(rocket_index)))

        try:
            yield from chain(flight, explosions)
        finally:
            self._on_board_sprites_drawer.discard_sprite(rocket_index)

    def _jump(self,
              sprite: arc.Sprite,
              from_coord: Vector2Int,
              to_coord: Vector2Int,
              height: float,
              duration: float) -> Animation:
        get_delta_position = self._get_jump_delta_position_getter(from_coord, to_coord, height, duration)
        return self._translate_sprite(sprite, get_delta_position, duration)

    def _get_jump_delta_position_getter(self,
                                        from_coord: Vector2Int,
                                        to_coord: Vector2Int,
                                        height: float,
                                        duration: float) -> Callable[[float], Vector2]:
        direction = get_direction(from_coord, to_coord, strict=False)
        start = get_world_position(from_coord)
        end = get_world_position(to_coord)

        def get_delta_position(t: float) -> Vector2:
            camera = self._camera

            t /= duration
            parabola = Parabola.from_points(Vector2.zero(),
                                            Vector2(.5, height),
                                            Vector2(1, 0))

            to_end = direction * (end - start).length() * t
            to_periapsis = camera.orientation.rotation.inverse.apply(Vector2.up()).normalize() * parabola.value(t)

            delta_position = to_end + to_periapsis
            return delta_position

        return get_delta_position

    def _play_sound(self, sound: proto.SoundPlayer) -> Animation:
        try:
            sound.play(self._speed_multiplier)
            while not sound.is_completed:
                yield
        finally:
            sound.stop()

    def _play_sound_fully(self, sound: proto.SoundPlayer) -> Animation:
        yield
        sound.play(self._speed_multiplier)

    def _get_sprite_at(self, coord: Vector2Int) -> arc.Sprite:
        return self._on_board_sprites_drawer.get_sprite(self._figures_drawer.get_figure_index(coord))

    def _sleep(self, duration: float) -> Animation:
        yield from sleep_gametime(duration / self._speed_multiplier, self._in_game_time)

    def _hide_figure(self, coord: Vector2Int) -> Animation:
        yield
        sprite = self._get_sprite_at(coord)
        sprite.scale = 0

    def _show_sprite(self,
                     sprite: proto.Sprite,
                     coord: Vector2Int,
                     duration: float,
                     *,
                     scale_ratio: float = 1) -> Animation:
        index = self._on_board_sprites_drawer.add_sprite(sprite, coord, scale_ratio=scale_ratio)
        try:
            yield from self._sleep(duration)
        finally:
            self._on_board_sprites_drawer.discard_sprite(index)

    def _translate_sprite(self,
                          sprite: arc.Sprite,
                          delta_position: Callable[[float], Vector2],
                          duration: float) -> Animation:
        yield
        sprite_position = Vector2(*sprite.position)
        start = self._in_game_time.get()

        def update_position() -> None:
            delta_time = self._in_game_time.get() - start
            sprite.position = (sprite_position + delta_position(delta_time * self._speed_multiplier)).tuple

        yield from group(self._sleep(duration), cycle(lambda: call(update_position)))

    def _rotate_sprite(self,
                       sprite: arc.Sprite,
                       delta_angle: Callable[[float], Angle],
                       duration: float) -> Animation:
        yield
        start = self._in_game_time.get()
        rotator = SpriteRotator(sprite, self._camera.orientation)
        self._camera.orientation.has_changed.subscribe(rotator.on_camera_orientation_changed)

        def update_rotation() -> None:
            delta_time = self._in_game_time.get() - start
            rotator.update(delta_angle(delta_time * self._speed_multiplier))

        yield from group(self._sleep(duration), cycle(lambda: call(update_rotation)))
        self._camera.orientation.has_changed.unsubscribe(rotator.on_camera_orientation_changed)

    def _resize_sprite(self,
                       sprite: arc.Sprite,
                       delta_size: Callable[[float], float],
                       duration: float) -> Animation:
        yield
        sprite_size = sprite.scale[0]
        ratio = sprite.scale[1] / sprite.scale[0]
        start = self._in_game_time.get()

        def update_size() -> None:
            delta_time = self._in_game_time.get() - start
            sprite.scale = (Vector2(1, ratio) * (sprite_size + delta_size(delta_time * self._speed_multiplier))).tuple

        yield from group(self._sleep(duration), cycle(lambda: call(update_size)))


@define
class SpriteRotator:
    _sprite: arc.Sprite
    _camera_orientation: proto.ReadonlyCameraOrientation

    _previous_camera_angle: Angle = field(init=False)
    _initial_sprite_angle: Angle = field(init=False)

    def __attrs_post_init__(self) -> None:
        self._initial_sprite_angle = Angle(self._sprite.angle)
        self._previous_camera_angle = self._camera_orientation.rotation

    def update(self, delta_angle: Angle) -> None:
        self._sprite.angle = (self._initial_sprite_angle + delta_angle).degrees

    def on_camera_orientation_changed(self) -> None:
        delta_angle = self._camera_orientation.rotation - self._previous_camera_angle
        self._previous_camera_angle = self._camera_orientation.rotation
        self._initial_sprite_angle += delta_angle
