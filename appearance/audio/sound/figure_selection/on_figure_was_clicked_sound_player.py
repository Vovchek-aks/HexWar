from attrs import define, field

import appearance.protocols as proto
from appearance.audio.sound.figure_selection.figures_sounds import FiguresSounds
from appearance.audio.sound.sounds_loader import SoundsLoader
from appearance.input.moves_inputer.input_actions import CellClickAction
from appearance.protocols import InputAction
from core.protocols import GameSession
import core.figures.figure as fig


@define
class OnFigureWasClickedSoundPlayer:
    @classmethod
    def make(cls,
             session: GameSession,
             figures_sounds: FiguresSounds,
             actions_reader: proto.InputActionsReader) -> "OnFigureWasClickedSoundPlayer":
        self = cls(session, figures_sounds)
        actions_reader.action_was_read.subscribe(lambda action, _: self._on_figure_was_clicked(action))
        return self

    _session: GameSession
    _figures_sounds: FiguresSounds

    _sound_player: proto.SoundPlayer = field(init=False, factory=lambda: SoundsLoader.from_meta().load_empty())
    _last_clicked_figure: type[fig.Figure] = fig.Land

    def _on_figure_was_clicked(self, action: InputAction) -> None:
        if not isinstance(action, CellClickAction):
            return

        if not action.buttons.is_left:
            return

        figure = type(self._session.board[action.coord].figure)
        if issubclass(figure, self._last_clicked_figure):
            self._sound_player.play()
            return

        self._last_clicked_figure = figure
        self._sound_player.stop()
        self._sound_player = self._figures_sounds.get_for(figure)
        self._sound_player.play()
