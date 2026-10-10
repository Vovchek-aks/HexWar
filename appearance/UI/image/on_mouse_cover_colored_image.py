from attrs import define, field

from appearance.UI.image import ImageUi
from appearance.graphics.sprites import Sprite
import appearance.protocols as proto
from appearance.input.clicks_catcher.click import MouseButtons, Click
from color import Color
from mathematics.rectangle import Rectangle
from mathematics.vector import Vector2Int


@define(hash=True)
class OnMouseCoverColoredImageUi(ImageUi):
    @classmethod
    def from_image(cls,
                   image: ImageUi,
                   color: Color,
                   mouse_movement_observer: proto.MouseMovementObserver) -> "OnMouseCoverColoredImageUi":
        self = cls(image._drawer, image.sprite, image.rectangle, image.sprite,
                   image.sprite.colored_in(color), color, mouse_movement_observer)
        mouse_movement_observer.mouse_was_moved.subscribe(lambda _: self._update_sprite())
        return self

    _default_sprite: Sprite = field(hash=False)
    _colored_sprite: Sprite = field(hash=False)
    _color: Color = field(hash=False)
    _mouse_movement_observer: proto.MouseMovementObserver = field(hash=False)

    @property
    def _need_to_color(self) -> bool:
        fake_click = Click(self._mouse_movement_observer.mouse_position, MouseButtons())
        return self.layer.can_catch(fake_click)

    def set_sprite(self, sprite: Sprite) -> None:
        self._default_sprite = self._reshape(sprite, self.rectangle)
        self._colored_sprite = self._default_sprite.colored_in(self._color)
        self._update_sprite()

    def set_rectangle(self, rectangle: Rectangle) -> None:
        super().set_rectangle(rectangle)
        self._default_sprite = self._default_sprite.reshape(Vector2Int.from_vector2(rectangle.shape, strict=False))
        self._colored_sprite = self._colored_sprite.reshape(Vector2Int.from_vector2(rectangle.shape, strict=False))

    def _update_sprite(self) -> None:
        self._sprite = self._colored_sprite if self._need_to_color else self._default_sprite
