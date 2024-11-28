from pygame import Vector2

from scenes.SPECIAL.Effects.Effect import Effect
from scripts.GameTypes import ColorNormalized, Percentage
from scripts.Utilities.Graphics.double_framebuffer import DoubleFramebuffer
from scripts.Utilities.Graphics.frag import Frag


class Vignette(Effect):
    def __init__(self, frag: Frag, vignette_color: ColorNormalized=(0, 0, 0), power: float=0.25):
        super().__init__(frag)

        self.tex: DoubleFramebuffer = self.graphics.double_fbo
        self.vignette_color: ColorNormalized = vignette_color
        self.power: float = power

    @property
    def clone(self) -> 'Vignette':
        return Vignette(self.frag, self.vignette_color, self.power)

    def _update_frag(self) -> None:
        self.frag.attributes = {
            "tex": self.tex,
            "vignette_color": self.vignette_color,
            "power": self.power
        }
