from pygame import Vector2
from scenes.SPECIAL.Effects.Effect import Effect
from scripts.GameTypes import ColorNormalized, Percentage
from scripts.Utilities.Graphics.double_framebuffer import DoubleFramebuffer
from scripts.Utilities.Graphics.frag import Frag

class Fisheye(Effect):
    def __init__(self, frag: Frag, zoom: float=0, fisheye_amount: float=0):
        super().__init__(frag)

        self.tex: DoubleFramebuffer = self.graphics.double_fbo
        self.zoom: float = zoom
        self.fisheye_amount: float = fisheye_amount

    @property
    def fisheye_distance(self) -> float:
        if self.fisheye_amount == 0:
            return 0

        return 1 / self.fisheye_amount

    @property
    def clone(self) -> 'Fisheye':
        return Fisheye(self.frag, self.zoom, self.fisheye_amount)

    def _update_frag(self) -> None:
        self.frag.attributes = {
            "tex": self.tex,
            "zoom": 2 ** -self.zoom,
            "fisheye_distance": self.fisheye_distance,
            "aspect_ratio": self.game.window.aspect_ratio,
            "aspect_ratio_inverse": self.game.window.aspect_ratio_inverse
        }
