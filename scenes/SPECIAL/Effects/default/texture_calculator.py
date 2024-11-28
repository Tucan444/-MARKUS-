from scenes.SPECIAL.Effects.Effect import Effect
from scripts.GameTypes import Percentage, OperationType
from scripts.Utilities.Graphics.double_framebuffer import DoubleFramebuffer
from scripts.Utilities.Graphics.frag import Frag


class TextureCalculator(Effect):

    def __init__(self, frag: Frag, a_amount: float=1, b_amount: float=1, interpolation: Percentage=0.5,
                 operation: OperationType=OperationType.ADD):
        super().__init__(frag)

        self.tex_a: DoubleFramebuffer = self.graphics.double_fbo
        self.tex_b: DoubleFramebuffer = self.graphics.double_fbo
        self.target: DoubleFramebuffer = self.graphics.double_fbo

        self.a_amount: float = a_amount
        self.b_amount: float = b_amount
        self.interpolation: Percentage = interpolation

        self.operation: OperationType = operation

    def flip_textures(self) -> None:
        self.tex_a, self.tex_b = self.tex_b, self.tex_a

    @property
    def clone(self) -> 'HazeBloom':
        calculator = TextureCalculator(self.frag, self.a_amount, self.b_amount, self.interpolation, self.operation)
        calculator.tex_a = self.tex_a
        calculator.tex_b = self.tex_b
        calculator.target = self.target

        return calculator

    @property
    def a_interpolated(self) -> float:
        return 2 * self.interpolation * self.a_amount

    @property
    def b_interpolated(self) -> float:
        return 2 * (1 - self.interpolation) * self.b_amount

    def _update_frag(self) -> None:
        self.frag.attributes = {
            "tex_a": self.tex_a,
            "tex_b": self.tex_b,
            "a_amount": self.a_interpolated,
            "b_amount": self.b_interpolated,
            "operation": self.operation.value
        }

    def _configure_frag(self) -> None:
        self.frag.target = self.target
