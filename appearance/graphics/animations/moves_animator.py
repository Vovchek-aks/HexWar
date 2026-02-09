from typing import Iterator, Callable
from time import time

from attrs import frozen

import appearance.protocols as proto
from appearance.graphics.sprites import SpritesLoader
from core.moves.attack import Attack
from core.protocols import Move
from mathematics.vector import Vector2Int
from statuses import Status, MISSING

Animation = Iterator[None]

ATTACK_EXPLOSION_DURATION = .3
ATTACK_EXPLOSION_SCALE_RATIO = 1.5


@frozen
class MovesAnimator(proto.MovesAnimator):
    @classmethod
    def make(cls,
             on_board_sprites_drawer: proto.OnBoardSpritesDrawer,
             *,
             speed_multiplier: float = 1) -> "MovesAnimator":
        sprites_loader = SpritesLoader.from_meta()
        self = cls(
            speed_multiplier,
            on_board_sprites_drawer,
            sprites_loader.load_explosion()
        )
        return self

    _speed_multiplier: float

    _on_board_sprites_drawer: proto.OnBoardSpritesDrawer
    _explosion: proto.Sprite

    def get_animation(self, move: Move) -> Animation | Status:
        match move:
            case Attack(to_coord=coord):
                return self._show_sprite(self._explosion, coord, ATTACK_EXPLOSION_DURATION,
                                         scale_ratio=ATTACK_EXPLOSION_SCALE_RATIO)
            case _:
                return MISSING
        assert False

    def _sleep(self, duration: float) -> Animation:
        yield from self._sleep_realtime(duration / self._speed_multiplier)

    def _show_sprite(self,
                     sprite: proto.Sprite,
                     coord: Vector2Int,
                     duration: float,
                     *,
                     scale_ratio: float = 1) -> Animation:
        index = self._on_board_sprites_drawer.add_sprite(sprite, coord, scale_ratio=scale_ratio)
        yield from self._sleep(duration)
        self._on_board_sprites_drawer.remove_sprite(index)

    @staticmethod
    def _sleep_realtime(duration: float) -> Animation:
        start = time()
        while time() - start < duration:
            yield

    @staticmethod
    def _call(function: Callable[[], None]) -> Animation:
        function()
        yield

    @staticmethod
    def _no_animation() -> Animation:
        yield


def _chain(*animations: Animation) -> Animation:
    for animation in animations:
        yield from animation


def _group(*animations: Animation, strict: bool = False) -> Animation:
    for frame in zip(*animations, strict=strict):
        for _ in frame:
            ...
        yield
