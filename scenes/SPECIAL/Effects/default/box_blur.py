from pygame import Vector2

from scenes.SPECIAL.Effects.Effect import Effect
from scripts.GameTypes import Scaling
from scripts.Utilities.Graphics.double_framebuffer import DoubleFramebuffer
from scripts.Utilities.Graphics.frag import Frag


class BoxBlur(Effect):
    def __init__(self, frag: Frag, blur_size: int=1, pixel_scale: float=1, pixel_scaling: Scaling=None,
                 x_pass: bool=True, y_pass: bool=True):
        super().__init__(frag)

        self.tex: DoubleFramebuffer = self.graphics.double_fbo
        self.blur_size: int = blur_size
        self.pixel_scale: float = pixel_scale
        self.pixel_scaling: Scaling = pixel_scaling if pixel_scaling is not None else Vector2(1, 1)
        self.x_pass: bool = x_pass
        self.y_pass: bool = y_pass

        self._forward_pass: bool = True

    @property
    def clone(self) -> 'BoxBlur':
        return BoxBlur(self.frag, self.blur_size, self.pixel_scale, self.pixel_scaling, self.x_pass, self.y_pass)

    @property
    def divider(self) -> float:
        return 1 / ((2 * self.blur_size) + 1)

    def _update_frag(self) -> None:
        pixel_size: Scaling = Vector2(
            self.graphics.UV_PIXEL_SIZE.x * self.pixel_scaling.x,
            self.graphics.UV_PIXEL_SIZE.y * self.pixel_scaling.y
        ) * self.pixel_scale

        self.frag.attributes = {
            "tex": self.tex,
            "blur_size": self.blur_size,
            "pixel_size": pixel_size,
            "divider": self.divider,
            "x_pass": 1 if self._forward_pass else 0,
            "y_pass": 0 if self._forward_pass else 1
        }

    def _execute_frag(self) -> None:
        self.frag.execute(reset_attributes=False)

        self._forward_pass = False
        self._update_frag()
        self.frag.execute()

        self._forward_pass = True
