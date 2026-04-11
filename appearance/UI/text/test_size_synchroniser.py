from attrs import define, field

from appearance.UI.text import TextUi


@define
class TextSizeSynchroniser:
    _texts: list[TextUi] = field(factory=list)
    _min_size: float = float("inf")

    def append(self, text: TextUi) -> None:
        self._texts.append(text)
        text.size_was_changed.subscribe(self._on_font_size_changed)
        self._on_font_size_changed(text)

    def extend(self, *texts: TextUi) -> None:
        for text in texts:
            self.append(text)

    def _on_font_size_changed(self, changed_text: TextUi) -> None:
        if changed_text.font_size == self._min_size:
            return

        if changed_text.font_size > self._min_size:
            self._min_size = min(text.font_size for text in self._texts)
            changed_text.set_font_size(self._min_size, need_event=False)
            return

        self._min_size = changed_text.font_size
        for text in self._texts:
            text.set_font_size(self._min_size)
