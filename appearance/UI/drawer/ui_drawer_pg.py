from attrs import frozen
import pygame as pg

import appearance.protocols as proto


@frozen
class UiDrawer(proto.UiDrawer):
    _screen: pg.Surface

    def draw_text(self, text_data: proto.TextData) -> None:
        text, font, color, position = text_data.tuple
        rendered = font.render(text, True, color)
        self._screen.blit(rendered, position)
