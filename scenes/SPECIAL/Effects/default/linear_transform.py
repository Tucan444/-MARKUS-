from pygame import Vector2

from scenes.SPECIAL.Effects.Effect import Effect
from scripts.GameTypes import ColorNormalized, Percentage, Scaling, DisplayVector, Angle, HyperAngle, Shear, UV_Position
from scripts.Utilities.Graphics.double_framebuffer import DoubleFramebuffer
from scripts.Utilities.Graphics.frag import Frag
from scripts.DataStructures.matrices import Matrix2D


class LinearTransform(Effect):
    def __init__(self, frag: Frag, offset: DisplayVector=None, scaling: Scaling=None,
                 rotate: Angle=0, hyper_rotate: HyperAngle=0, shear: Shear=None):
        super().__init__(frag)

        self.tex: DoubleFramebuffer = self.graphics.double_fbo
        self.offset: DisplayVector = offset if offset is not None else Vector2()
        self.scaling: Scaling = scaling if scaling is not None else Vector2(1, 1)
        self.rotate: Angle = rotate
        self.hyper_rotate: HyperAngle = hyper_rotate
        self.shear: Shear = shear if shear is not None else (Vector2(0, 0), True)

    @property
    def transform_matrix(self) -> Matrix2D:
        scale_matrix: Matrix2D = Matrix2D.get_scale(*Vector2(1 / self.scaling.x, 1 / self.scaling.y))
        rotate_matrix: Matrix2D = Matrix2D.get_rotation(self.rotate)
        hyper_rotate_matrix: Matrix2D = Matrix2D.get_hyperbolic_rotation(self.hyper_rotate)
        shear_matrix: Matrix2D = Matrix2D.get_shear(*(-self.shear[0]), self.shear[1])

        final_matrix: Matrix2D = scale_matrix.before(rotate_matrix).before(hyper_rotate_matrix).before(shear_matrix)
        return final_matrix

    @property
    def uv_position_offset(self) -> UV_Position:
        uv_position: UV_Position = self.graphics.position_display_to_uv(self.offset)
        uv_position.x *= -1
        return uv_position

    @property
    def clone(self) -> 'LinearTransform':
        return LinearTransform(self.frag, self.offset, self.scaling, self.rotate, self.hyper_rotate)

    def _update_frag(self) -> None:
        self.frag.attributes = {
            "tex": self.tex,
            "offset": self.uv_position_offset,
            "transform": self.transform_matrix,
            "aspect_ratio": self.game.window.aspect_ratio,
            "aspect_ratio_inverse": self.game.window.aspect_ratio_inverse
        }
