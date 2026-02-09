from typing import Iterator, Callable
from time import perf_counter as time
from itertools import chain

from attrs import frozen
import arcade as arc

import appearance.protocols as proto
from appearance.graphics.sprites import SpritesLoader
from core.moves.attack import Attack
from core.moves.relocations import Assault, Relocation
from core.protocols import Move
from mathematics.hex_geometry import get_world_position, DISTANCE_BETWEEN_CENTERS, get_direction
from mathematics.parabola import Parabola
from mathematics.vector import Vector2Int, Vector2
from statuses import Status, MISSING

Animation = Iterator[None]

ATTACK_EXPLOSION_DURATION = .3
ATTACK_EXPLOSION_SCALE_RATIO = 1.5
ATTACK_KICKBACK_DURATION = .1
ATTACK_KICKBACK_RETURN_DURATION = .2
ATTACK_KICKBACK_DELTA_POSITION = DISTANCE_BETWEEN_CENTERS / 4

RELOCATION_JUMP_DURATION = .2
RELOCATION_JUMP_HEIGHT = DISTANCE_BETWEEN_CENTERS / 2


@frozen
class MovesAnimator(proto.MovesAnimator):
    @classmethod
    def make(cls,
             on_board_sprites_drawer: proto.OnBoardSpritesDrawer,
             figures_drawer: proto.FiguresDrawer,
             camera: proto.Camera,
             *,
             speed_multiplier: float = 1) -> "MovesAnimator":
        sprites_loader = SpritesLoader.from_meta()
        self = cls(
            speed_multiplier,
            figures_drawer,
            camera,
            on_board_sprites_drawer,
            sprites_loader.load_explosion()
        )
        return self

    _speed_multiplier: float

    _figures_drawer: proto.FiguresDrawer
    _camera: proto.Camera

    _on_board_sprites_drawer: proto.OnBoardSpritesDrawer
    _explosion: proto.Sprite

    def get_animation(self, move: Move) -> Animation | Status:
        match move:
            case Attack(from_coord=coord, to_coord=target):
                return self._get_attack_animation(coord, target)
            case (Relocation(from_coord=from_coord, to_coord=to_coord) |
                  Assault(from_coord=from_coord, to_coord=to_coord)):
                return self.get_relocation_animation(from_coord, to_coord)
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
        artillery = self.get_sprite_at(coord)
        artillery_position = artillery.position
        kickback = chain(self._translate_sprite(artillery, lambda t: delta * t / ATTACK_KICKBACK_DURATION,
                                                ATTACK_KICKBACK_DURATION),
                         _call(lambda: _set_sprite_position(artillery, artillery_position + delta)),
                         self._translate_sprite(artillery, lambda t: -delta * t / ATTACK_KICKBACK_RETURN_DURATION,
                                                ATTACK_KICKBACK_RETURN_DURATION),
                         _call(lambda: self._figures_drawer.update_cell(coord)))
        return _group(explosion, kickback)

    def get_relocation_animation(self, from_coord: Vector2Int, to_coord: Vector2Int) -> Animation:
        figure = self.get_sprite_at(from_coord)
        direction = get_direction(from_coord, to_coord)
        start = get_world_position(from_coord)
        end = get_world_position(to_coord)

        def get_delta_position(t: float) -> Vector2:
            camera = self._camera

            t /= RELOCATION_JUMP_DURATION
            parabola = Parabola.from_points(Vector2.zero(),
                                            Vector2(.5, RELOCATION_JUMP_HEIGHT),
                                            Vector2(1, 0))

            to_end = direction * (end - start).length() * t
            to_periapsis = -camera.screen_to_world(Vector2.up()).normalize() * parabola.value(t)

            delta_position = to_end + to_periapsis
            return delta_position

        return self._translate_sprite(figure, get_delta_position, RELOCATION_JUMP_DURATION)

    def get_sprite_at(self, coord: Vector2Int) -> arc.Sprite:
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
        sprite_position = Vector2(*sprite.position)
        start = time()

        def update_position() -> None:
            delta_time = time() - start
            sprite.position = (sprite_position + delta_position(delta_time * self._speed_multiplier)).tuple

        yield from _group(self._sleep(duration), _cycle(lambda: _call(update_position)))


def _sleep_realtime(duration: float) -> Animation:
    start = time()
    while time() - start < duration:
        yield


def _call(function: Callable[[], None]) -> Animation:
    function()
    yield


def _cycle(get_animation: Callable[[], Animation]) -> Animation:
    while True:
        yield from get_animation()


def _no_animation() -> Animation:
    yield


def _group(*animations: Animation, strict: bool = False) -> Animation:
    for frame in zip(*animations, strict=strict):
        for _ in frame:
            ...
        yield
