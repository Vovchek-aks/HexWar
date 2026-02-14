from typing import Iterator, Callable
from time import perf_counter as time
from itertools import chain

from attrs import frozen
import arcade as arc

import appearance.protocols as proto
from appearance.graphics.sprites import SpritesLoader
from core.moves.attack import Attack
from core.moves.capture import Capture
from core.moves.creation import Creation
from core.moves.relocations import Assault, Relocation
from core.protocols import Move, GameSession, Figure
from mathematics.angle import Angle
from mathematics.hex_geometry import get_world_position, DISTANCE_BETWEEN_CENTERS, get_direction
from mathematics.parabola import Parabola
from mathematics.vector import Vector2Int, Vector2
from statuses import Status, MISSING

ATTACK_EXPLOSION_DURATION = .3
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

CREATION_DURATION = .5
CREATION_FIRST_JUMP_DURATION_RATIO = .6
CREATION_FIRST_JUMP_HEIGHT = DISTANCE_BETWEEN_CENTERS / 3
CREATION_SECOND_JUMP_HEIGHT = DISTANCE_BETWEEN_CENTERS / 8
CREATION_INITIAL_SCALE_RATIO = 0.2
CREATION_FINAL_SCALE_RATIO = 1.1

Animation = Iterator[None]


@frozen
class MovesAnimator(proto.MovesAnimator):
    @classmethod
    def make(cls,
             on_board_sprites_drawer: proto.OnBoardSpritesDrawer,
             figures_drawer: proto.FiguresDrawer,
             camera: proto.Camera,
             session: GameSession,
             *,
             speed_multiplier: float = 1) -> "MovesAnimator":
        sprites_loader = SpritesLoader.from_meta()
        self = cls(
            speed_multiplier,
            figures_drawer,
            camera,
            session,
            on_board_sprites_drawer,
            sprites_loader.load_explosion()
        )
        return self

    _speed_multiplier: float

    _figures_drawer: proto.FiguresDrawer
    _camera: proto.Camera
    _session: GameSession

    _on_board_sprites_drawer: proto.OnBoardSpritesDrawer
    _explosion: proto.Sprite

    def get_animation(self, move: Move) -> Animation | Status:
        if self._speed_multiplier == float('inf'):
            return MISSING

        match move:
            case Attack(from_coord=coord, to_coord=target):
                return self._get_attack_animation(coord, target)
            case (Relocation(from_coord=from_coord, to_coord=to_coord) |
                  Assault(from_coord=from_coord, to_coord=to_coord)):
                animation = self._get_relocation_animation(from_coord, to_coord)
                if (pullable := move.pullable_cell(self._session)) is MISSING:
                    return animation
                pulling = self._get_relocation_animation(self._session.board.coordinates_of(pullable), from_coord)
                return _group(chain(animation, _cycle(_no_animation)),
                              chain(self._sleep(RELOCATION_PULLING_LAG), pulling))
            case Capture(to_coord=coord):
                return self._get_capture_animation(coord)
            case Creation(to_coord=coord, figure_type=figure):
                return self._get_creation_animation(coord, figure)
            case _:
                return MISSING
        assert False

    def _get_attack_animation(self, coord: Vector2Int, target: Vector2Int) -> Animation:
        explosion = chain(self._show_sprite(self._explosion, target, ATTACK_EXPLOSION_DURATION,
                                            scale_ratio=ATTACK_EXPLOSION_SCALE_RATIO),
                          _cycle(_no_animation))

        def _set_sprite_position(sprite: arc.Sprite, position: Vector2) -> None:
            sprite.position = position

        delta = -ATTACK_KICKBACK_DELTA_POSITION * get_direction(coord, target)
        artillery = self._get_sprite_at(coord)
        artillery_position = artillery.position
        kickback = chain(self._translate_sprite(artillery, lambda t: delta * t / ATTACK_KICKBACK_DURATION,
                                                ATTACK_KICKBACK_DURATION),
                         _call(lambda: _set_sprite_position(artillery, artillery_position + delta)),
                         self._translate_sprite(artillery, lambda t: -delta * t / ATTACK_KICKBACK_RETURN_DURATION,
                                                ATTACK_KICKBACK_RETURN_DURATION),
                         _call(lambda: self._figures_drawer.update_cell(coord)))
        return _group(explosion, kickback)

    def _get_relocation_animation(self, from_coord: Vector2Int, to_coord: Vector2Int) -> Animation:
        return self._jump(self._get_sprite_at(from_coord), from_coord, to_coord,
                          RELOCATION_JUMP_HEIGHT, RELOCATION_JUMP_DURATION)

    def _get_capture_animation(self, coord: Vector2Int) -> Animation:
        sprite = self._get_sprite_at(coord)
        initial_rotation = Angle(sprite.angle)
        shaking_duration = CAPTURE_DURATION * CAPTURE_SHAKING_DURATION_RATIO
        resizing_duration = (CAPTURE_DURATION - shaking_duration) / 2
        size_changing_speed = (CAPTURE_SCALE_RATIO - 1) * sprite.scale[0] / resizing_duration
        angle_changing_speed = CAPTURE_SHAKE_ANGLE * (1 / resizing_duration)
        shaking_angle_changing_speed = CAPTURE_SHAKE_ANGLE * (1 / shaking_duration)

        def set_rotation(rotation: Angle) -> None:
            sprite.angle = rotation.degrees

        return chain(_group(self._resize_sprite(sprite, lambda t: size_changing_speed * t, resizing_duration),
                            self._rotate_sprite(sprite, lambda t: angle_changing_speed * t, resizing_duration)),
                     _call(lambda: set_rotation(initial_rotation + CAPTURE_SHAKE_ANGLE)),
                     self._rotate_sprite(sprite, lambda t: shaking_angle_changing_speed * -t * 6, shaking_duration / 3),
                     _call(lambda: set_rotation(initial_rotation + -CAPTURE_SHAKE_ANGLE)),
                     self._rotate_sprite(sprite, lambda t: shaking_angle_changing_speed * t * 6, shaking_duration / 3),
                     _call(lambda: set_rotation(initial_rotation + CAPTURE_SHAKE_ANGLE)),
                     self._rotate_sprite(sprite, lambda t: shaking_angle_changing_speed * -t * 6, shaking_duration / 3),
                     _call(lambda: set_rotation(initial_rotation + -CAPTURE_SHAKE_ANGLE)),
                     _group(self._resize_sprite(sprite, lambda t: -size_changing_speed * t, resizing_duration),
                            self._rotate_sprite(sprite, lambda t: angle_changing_speed * t, resizing_duration)),
                     _call(lambda: self._figures_drawer.update_cell(coord)))

    def _get_creation_animation(self, coord: Vector2Int, figure_type: type[Figure]) -> Animation:
        figure = self._figures_drawer.figures_sprites.get(figure_type)
        sprite_index = self._on_board_sprites_drawer.add_sprite(figure, coord, scale_ratio=CREATION_INITIAL_SCALE_RATIO)
        sprite = self._on_board_sprites_drawer.get_sprite(sprite_index)

        first_jump_duration = CREATION_DURATION * CREATION_FIRST_JUMP_DURATION_RATIO
        second_jump_duration = CREATION_DURATION - first_jump_duration

        first_resizing_speed = (sprite.scale[0] *
                                (CREATION_FINAL_SCALE_RATIO / CREATION_INITIAL_SCALE_RATIO - 1))
        second_resizing_speed = (sprite.scale[0] *
                                 (CREATION_FINAL_SCALE_RATIO / CREATION_INITIAL_SCALE_RATIO) *
                                 (1 / CREATION_FINAL_SCALE_RATIO - 1) /
                                 second_jump_duration)

        try:
            yield from chain(_group(self._jump(sprite, coord, coord, CREATION_FIRST_JUMP_HEIGHT, first_jump_duration),
                                    self._resize_sprite(sprite,
                                                        lambda t: first_resizing_speed * (t / first_jump_duration) ** 2,
                                                        first_jump_duration)),
                             _group(self._jump(sprite, coord, coord, CREATION_SECOND_JUMP_HEIGHT, second_jump_duration),
                                    self._resize_sprite(sprite, lambda t: second_resizing_speed * t,
                                                        second_jump_duration)))
        finally:
            self._on_board_sprites_drawer.remove_sprite(sprite_index)

    def _jump(self,
              sprite: arc.Sprite,
              from_coord: Vector2Int,
              to_coord: Vector2Int,
              height: float,
              duration: float) -> Animation:
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

        return self._translate_sprite(sprite, get_delta_position, duration)

    def _get_sprite_at(self, coord: Vector2Int) -> arc.Sprite:
        return self._on_board_sprites_drawer.get_sprite(self._figures_drawer.get_figure_index(coord))

    def _sleep(self, duration: float) -> Animation:
        yield from _sleep_realtime(duration / self._speed_multiplier)

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
            self._on_board_sprites_drawer.remove_sprite(index)

    def _translate_sprite(self,
                          sprite: arc.Sprite,
                          delta_position: Callable[[float], Vector2],
                          duration: float) -> Animation:
        yield
        sprite_position = Vector2(*sprite.position)
        start = time()

        def update_position() -> None:
            delta_time = time() - start
            sprite.position = (sprite_position + delta_position(delta_time * self._speed_multiplier)).tuple

        yield from _group(self._sleep(duration), _cycle(lambda: _call(update_position)))

    def _rotate_sprite(self,
                       sprite: arc.Sprite,
                       delta_angle: Callable[[float], Angle],
                       duration: float) -> Animation:
        yield
        sprite_angle = Angle(sprite.angle)
        start = time()

        def update_rotation() -> None:
            delta_time = time() - start
            sprite.angle = (sprite_angle + delta_angle(delta_time * self._speed_multiplier)).degrees

        yield from _group(self._sleep(duration), _cycle(lambda: _call(update_rotation)))

    def _resize_sprite(self,
                       sprite: arc.Sprite,
                       delta_size: Callable[[float], float],
                       duration: float) -> Animation:
        yield
        sprite_size = sprite.scale[0]
        ratio = sprite.scale[1] / sprite.scale[0]
        start = time()

        def update_size() -> None:
            delta_time = time() - start
            sprite.scale = (Vector2(1, ratio) * (sprite_size + delta_size(delta_time * self._speed_multiplier))).tuple

        yield from _group(self._sleep(duration), _cycle(lambda: _call(update_size)))


def _sleep_realtime(duration: float) -> Animation:
    yield
    start = time()
    while time() - start < duration:
        yield


def _call(function: Callable[[], None]) -> Animation:
    yield
    function()


def _cycle(get_animation: Callable[[], Animation]) -> Animation:
    while True:
        yield from get_animation()


def _no_animation() -> Animation:
    yield


def _group(*animations: Animation, strict: bool = False) -> Animation:
    for _ in zip(*animations, strict=strict):
        yield
