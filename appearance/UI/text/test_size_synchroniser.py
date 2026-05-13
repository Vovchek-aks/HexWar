from attrs import frozen, field

from appearance.UI.text import TextUi


@frozen
class TextSizeSynchroniser:
    _texts: list[TextUi] = field(factory=list)

    @property
    def size(self) -> float:
        return min(text.font_size for text in self._texts)

    def append(self, text: TextUi) -> None:
        self._texts.append(text)

    def extend(self, *texts: TextUi) -> None:
        for text in texts:
            self.append(text)

    def synchronise(self, size: float = float('inf')) -> None:
        min_size = min(size, self.size)
        for text in self._texts:
            text.set_font_size(min_size, need_event=False)
