from typing import Iterator, Callable
from time import perf_counter as time
from itertools import chain

from attrs import frozen
import arcade as arc

import appearance.protocols as proto
from appearance.graphics.sprites import SpritesLoader
from core.moves.attack import Attack
from core.protocols import Move
from mathematics.hex_geometry import get_world_position, DISTANCE_BETWEEN_CENTERS
from mathematics.vector import Vector2Int, Vector2
from statuses import Status, MISSING

Animation = Iterator[None]

ATTACK_EXPLOSION_DURATION = .3
ATTACK_EXPLOSION_SCALE_RATIO = 1.5
ATTACK_KICKBACK_DURATION = .05
ATTACK_KICKBACK_RETURN_DURATION = .2
ATTACK_KICKBACK_DELTA_POSITION = DISTANCE_BETWEEN_CENTERS / 4


@frozen
class MovesAnimator(proto.MovesAnimator):
    @classmethod
    def make(cls,
             on_board_sprites_drawer: proto.OnBoardSpritesDrawer,
             figures_drawer: proto.FiguresDrawer,
             *,
             speed_multiplier: float = 1) -> "MovesAnimator":
        sprites_loader = SpritesLoader.from_meta()
        self = cls(
            speed_multiplier,
            figures_drawer,
            on_board_sprites_drawer,
            sprites_loader.load_explosion()
        )
        return self

    _speed_multiplier: float

    _figures_drawer: proto.FiguresDrawer

    _on_board_sprites_drawer: proto.OnBoardSpritesDrawer
    _explosion: proto.Sprite

    def get_animation(self, move: Move) -> Animation | Status:
        match move:
            case Attack(from_coord=coord, to_coord=target):
                return self._get_attack_animation(coord, target)
            case _:
                return MISSING
        assert False

    def _get_attack_animation(self, coord: Vector2Int, target: Vector2Int) -> Animation:
        explosion = chain(self._show_sprite(self._explosion, target, ATTACK_EXPLOSION_DURATION,
                                            scale_ratio=ATTACK_EXPLOSION_SCALE_RATIO),
                          _cycle(_no_animation))

        def _teleport_sprite(sprite: arc.Sprite, position: Vector2) -> None:
            sprite.position = position

        delta = -ATTACK_KICKBACK_DELTA_POSITION * (get_world_position(target) - get_world_position(coord)).normalize()
        artillery = self._on_board_sprites_drawer.get_sprite(self._figures_drawer.get_figure_index(coord))
        artillery_position = artillery.position
        kickback = chain(self._translate_sprite(artillery, delta, ATTACK_KICKBACK_DURATION),
                         _call(lambda: _teleport_sprite(artillery, artillery_position + delta)),
                         self._translate_sprite(artillery, -delta, ATTACK_KICKBACK_RETURN_DURATION),
                         _call(lambda: self._figures_drawer.update_cell(coord)))
        return _group(explosion, kickback)

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

    def _translate_sprite(self, sprite: arc.Sprite, delta_position: Vector2, duration: float) -> Animation:
        velocity = delta_position / duration * self._speed_multiplier
        sprite_position = Vector2(*sprite.position)
        start = time()

        def update_position() -> None:
            sprite.position = (sprite_position + velocity * (time() - start)).tuple

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
