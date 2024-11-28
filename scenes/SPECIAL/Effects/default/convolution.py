import math

from moderngl import Texture
from pygame import Vector2, Vector3

from scenes.SPECIAL.Effects.Effect import Effect
from scripts.GameTypes import Scaling, Resolution
from scripts.Utilities.Graphics.double_framebuffer import DoubleFramebuffer
from scripts.Utilities.Graphics.frag import Frag
from scripts.Utilities.Graphics.kernel import Kernel


class Convolution(Effect):
    def __init__(self, frag: Frag, kernel: Texture=None, pixel_scale: float=1, pixel_scaling: Scaling=None,
                 kernel_color_range: float=255, release_kernel_on_del: bool=True):
        super().__init__(frag)

        self.tex: DoubleFramebuffer = self.graphics.double_fbo
        self.kernel: Texture = kernel if kernel is not None else self.graphics.white
        self.pixel_scale: float = pixel_scale
        self.pixel_scaling: Scaling = pixel_scaling if pixel_scaling is not None else Vector2(1, 1)
        self.kernel_color_range: float = kernel_color_range

        self.release_kernel_on_del: bool = release_kernel_on_del

    def __del__(self) -> None:
        if self.release_kernel_on_del:
            self.kernel.release()

    @property
    def clone(self) -> 'Convolution':
        return Convolution(self.frag, self.kernel, self.pixel_scale, self.pixel_scaling,
                           self.kernel_color_range, self.release_kernel_on_del)

    @property
    def color_range_zero(self) -> Vector3:
        return Vector3(Kernel.ZERO_MULTIPLIER * self.kernel_color_range)

    def _update_frag(self) -> None:
        pixel_size: Scaling = Vector2(
            self.graphics.UV_PIXEL_SIZE.x * self.pixel_scaling.x,
            self.graphics.UV_PIXEL_SIZE.y * self.pixel_scaling.y
        ) * self.pixel_scale

        kernel_pixel_size: Scaling = Vector2(
            1 / self.kernel.width,
            1 / self.kernel.height
        )

        x_shift: int = math.floor(self.kernel.width * 0.5)
        y_shift: int = math.floor(self.kernel.height * 0.5)

        kernel_x_range: Resolution = (-x_shift, self.kernel.width - x_shift)
        kernel_y_range: Resolution = (-y_shift, self.kernel.height - y_shift)

        self.frag.attributes = {
            "tex": self.tex,
            "kernel": self.kernel,
            "pixel_size": pixel_size,
            "kernel_pixel_size": kernel_pixel_size,

            "kernel_x_range": kernel_x_range,
            "kernel_y_range": kernel_y_range,
            "color_range": self.kernel_color_range,
            "color_range_zero": self.color_range_zero
        }
