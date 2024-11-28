from pygame import Vector2
from scenes.SPECIAL.Effects.Effect import Effect
from scripts.GameTypes import ColorNormalized, Percentage, UV_Position, PrisonShape
from scripts.Utilities.Graphics.double_framebuffer import DoubleFramebuffer
from scripts.Utilities.Graphics.frag import Frag


class Prison(Effect):
    def __init__(self, frag: Frag, obscure_color: ColorNormalized=(0, 0, 0), obscure: Percentage=0,
                 obscure_shape: PrisonShape=0, bar_color: ColorNormalized=(0, 0, 0), imprisonment: Percentage=0,
                 bar_shape: PrisonShape=0, repeatance: float=6, obscure_last: bool=True):

        super().__init__(frag)

        self.tex: DoubleFramebuffer = self.graphics.double_fbo
        self.obscure_color: ColorNormalized = obscure_color
        self.obscure: Percentage = obscure
        self.obscure_shape: PrisonShape = obscure_shape

        self.bar_color: ColorNormalized = bar_color
        self.imprisonment: Percentage = imprisonment
        self.bar_shape: PrisonShape = bar_shape
        self.repeatance: float = repeatance

        self.obscure_last: bool = obscure_last

        self._corrected_uv_mid: Vector2 = Vector2(self.game.window.aspect_ratio * 0.5, 0.5)
        self._base_circle_length: float = self._corrected_uv_mid.length()
        self._base_square_length: float = max(self._corrected_uv_mid)
        self._base_diamond_length: float = sum(self._corrected_uv_mid)

        self._sqrt2 = 2 ** 0.5


    @property
    def clone(self) -> 'Prison':
        return Prison(self.frag, self.obscure_color, self.obscure, self.obscure_shape,
                      self.bar_color, self.imprisonment, self.bar_shape, self.repeatance, self.obscure_last)

    @property
    def clear_distance(self) -> float:
        base_length: float = 0.01

        if self.obscure_shape == PrisonShape.CIRCLE:
            base_length = self._base_circle_length
        elif self.obscure_shape == PrisonShape.SQUARE:
            base_length = self._base_square_length
        elif self.obscure_shape == PrisonShape.DIAMOND:
            base_length = self._base_diamond_length

        return base_length

    @property
    def processed_imprisonment(self) -> float:
        processed_imprisonment: float = self.imprisonment * 0.51

        if self.bar_shape == PrisonShape.CIRCLE:
            processed_imprisonment *= self._sqrt2
        elif self.bar_shape == PrisonShape.SQUARE:
            pass
        elif self.bar_shape == PrisonShape.DIAMOND:
            processed_imprisonment *= 2

        return processed_imprisonment

    def _update_frag(self) -> None:

        self.frag.attributes = {
            "tex": self.tex,
            "obscure_last": 1 if self.obscure_last else 0,

            "obscure_color": self.obscure_color,
            "obscure": 1 - self.obscure,
            "obscure_shape": self.obscure_shape.value,
            "clear_distance": self.clear_distance,

            "bar_color": self.bar_color,
            "imprisonment": self.processed_imprisonment,
            "bar_shape": self.bar_shape.value,
            "repeatance": self.repeatance,

            "aspect_ratio": self.game.window.aspect_ratio
        }
