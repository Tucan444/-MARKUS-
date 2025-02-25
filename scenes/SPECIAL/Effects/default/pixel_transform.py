from pygame import Vector2

from scenes.SPECIAL.Effects.Effect import Effect
from scripts.GameTypes import ColorNormalized, Percentage, RealPercentage
from scripts.Utilities.Graphics.double_framebuffer import DoubleFramebuffer
from scripts.Utilities.Graphics.frag import Frag


class PixelTransform(Effect):
    def __init__(self, frag: Frag, add: ColorNormalized=(0, 0, 0), intensity: ColorNormalized=(1, 1, 1),
                 invert_color: Percentage=0, grayscale: Percentage=0, dynamic_range: float=0,
                 gamma: float=1, hue_shift: float=0, saturation_change: float=0):
        super().__init__(frag)

        self.tex: DoubleFramebuffer = self.graphics.double_fbo
        self.add: ColorNormalized = add
        self.intensity: ColorNormalized = intensity
        self.invert_color: Percentage = invert_color
        self.grayscale: Percentage = grayscale
        self.dynamic_range: float = dynamic_range
        self.gamma: float = gamma
        self.hue_shift: float = hue_shift
        self.saturation_change: RealPercentage = saturation_change

    @property
    def dynamic_range_inverse(self) -> float:
        if self.dynamic_range == 0:
            return -1

        return 1 / self.dynamic_range

    @property
    def clone(self) -> 'PixelTransform':
        return PixelTransform(self.frag, self.add, self.intensity,
                              self.invert_color, self.grayscale, self.dynamic_range,
                              self.gamma, self.hue_shift, self.saturation_change)

    def _update_frag(self) -> None:
        self.frag.attributes = {
            "tex": self.tex,
            "add": (*self.add, 0),
            "intensity": (*self.intensity, 1),
            "invert_color": self.invert_color,
            "grayscale": self.grayscale,
            "dynamic_range": self.dynamic_range,
            "dynamic_range_inverse": self.dynamic_range_inverse,
            "gamma": self.gamma,
            "hue_shift": self.hue_shift % 1,
            "saturation_change": self.saturation_change
        }
