import moderngl
from pygame import Vector2

from scenes.SPECIAL.Effects.Effect import Effect
from scripts.GameTypes import ColorNormalized, Percentage, Scaling, DisplayVector, Angle, HyperAngle, Shear, UV_Position
from scripts.Utilities.Graphics.double_framebuffer import DoubleFramebuffer
from scripts.Utilities.Graphics.frag import Frag
from scripts.DataStructures.matrices import Matrix2D


class HazeBloom(Effect):
    def __init__(self, frag: Frag, blur_size: int=0, threshold: Percentage=0,
                 bloom_color: ColorNormalized=(1, 1, 1), bloom_strength: float=1):
        super().__init__(frag)

        self.tex: DoubleFramebuffer = self.graphics.double_fbo
        self.box_blur: 'BoxBlur' = None
        self.pixel_transform: 'PixelTransform' = None

        self.calculation_target: DoubleFramebuffer = None
        self.blur_size: int = blur_size
        self.threshold: Percentage = threshold
        self.bloom_color: ColorNormalized = bloom_color
        self.bloom_strength: float = bloom_strength

        self._persistent_target: DoubleFramebuffer = None

    def init(self) -> None:
        self.box_blur = self.graphics.effects["box_blur"].clone
        self.pixel_transform = self.graphics.effects["pixel_transform"].clone

    @property
    def clone(self) -> 'HazeBloom':
        haze_bloom = HazeBloom(self.frag, self.blur_size, self.threshold, self.bloom_color, self.bloom_strength)
        haze_bloom.target = self.calculation_target
        haze_bloom.init()

        return haze_bloom

    def _update_frag(self) -> None:
        if self.calculation_target is None:
            raise Exception("target of HazeBloom not assigned")

        self.frag.attributes = {
            "tex": self.tex,
            "threshold": self.threshold
        }

        self.box_blur.tex = self.calculation_target
        self.box_blur.blur_size = self.blur_size

        self.pixel_transform.tex = self.calculation_target
        self.pixel_transform.intensity = (
            self.bloom_color[0] * self.bloom_strength,
            self.bloom_color[1] * self.bloom_strength,
            self.bloom_color[2] * self.bloom_strength
        )

    def _configure_frag(self) -> None:
        self._persistent_target = self.frag.target
        self.frag.target = self.calculation_target
        self.frag.flip_fbo = False

    def _execute_frag(self) -> None:
        self.frag.execute()

        self.box_blur.frag.target = self.calculation_target
        self.box_blur.execute()

        self.pixel_transform.frag.target = self.calculation_target
        self.pixel_transform.execute()

        self._persistent_target.use()
        self.graphics.blit_texture(Vector2(), self.calculation_target.front, alpha=1, funcs=(
            moderngl.ONE, moderngl.ONE
        ))
