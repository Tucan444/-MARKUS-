from scenes.SPECIAL.Effects.Effect import Effect
from scripts.GameTypes import ColorNormalized
from scripts.Utilities.Graphics.double_framebuffer import DoubleFramebuffer
from scripts.Utilities.Graphics.frag import Frag


class FilmGrain(Effect):
    def __init__(self, frag: Frag, grain_color: ColorNormalized=(1, 1, 1), grain_amount: float=0.2):
        super().__init__(frag)

        self.tex: DoubleFramebuffer = self.graphics.double_fbo
        self.grain_color: ColorNormalized = grain_color
        self.grain_amount: float = grain_amount

    @property
    def clone(self) -> 'FilmGrain':
        return FilmGrain(self.frag, self.grain_color, self.grain_amount)

    def _update_frag(self) -> None:
        self.frag.attributes = {
            "tex": self.tex,
            "grain_color": self.grain_color,
            "grain_amount": self.grain_amount,
            "time": self.game.flow.dt
        }
