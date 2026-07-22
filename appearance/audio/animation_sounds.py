from attrs import frozen

from appearance.protocols import SoundPlayer
import core.figures.figure as fig


@frozen
class AnimationSounds:
    _no_sound: SoundPlayer
    _creation_landing: SoundPlayer
    _pulling_initiation: SoundPlayer
    _conversion: SoundPlayer
    _capture: SoundPlayer
    _oreshnik_flight: SoundPlayer
    _explosion: SoundPlayer
    _attack: SoundPlayer
    _relocation_infantry: SoundPlayer
    _relocation_motorization: SoundPlayer
    _relocation_tank: SoundPlayer
    _relocation_howitzer: SoundPlayer

    @property
    def creation_landing(self) -> SoundPlayer:
        return self._creation_landing

    @property
    def pulling_initiation(self) -> SoundPlayer:
        return self._pulling_initiation

    @property
    def conversion(self) -> SoundPlayer:
        return self._conversion

    @property
    def capture(self) -> SoundPlayer:
        return self._capture

    @property
    def oreshnik_flight(self) -> SoundPlayer:
        return self._oreshnik_flight

    @property
    def explosion(self) -> SoundPlayer:
        return self._explosion

    @property
    def attack(self) -> SoundPlayer:
        return self._attack

    def relocation_for(self, figure: type[fig.Figure]) -> SoundPlayer:
        sound_for: dict[type[fig.Figure], SoundPlayer] = {
            fig.Infantry: self._relocation_infantry,
            fig.Artillery: self._relocation_infantry,
            fig.Motorization: self._relocation_motorization,
            fig.Tank: self._relocation_tank,
            fig.Howitzer: self._relocation_howitzer,
        }
        return sound_for.get(figure, self._no_sound)
