import time

import moderngl
from moderngl import Program, Context, VertexArray, Texture, Framebuffer
from pygame import Vector2, Vector3

from scripts.DataStructures.matrices import Matrix2D, Matrix3D
from scripts.GameTypes import Viewport, ShaderAttributes
from scripts.Utilities.Graphics.double_framebuffer import DoubleFramebuffer


class Frag:
    def __init__(self, game: 'Game', program: Program):
        self.game: 'Game' = game
        self.graphics: 'Graphics' = self.game.graphics
        self.ctx: Context = self.game.graphics.ctx
        self.program: Program = program
        self.attributes: ShaderAttributes = {}

        self.target: DoubleFramebuffer = self.graphics.double_fbo
        self.viewport: Viewport | None = self.graphics.default_viewport
        self.flip_fbo: bool = True

        self.vao: VertexArray = self.ctx.vertex_array(self.program, [
            (self.graphics.quad_vertices, '2f', 'position'),
            (self.graphics.effect_uvs, '2f', 'texcoord')
        ])

    def __del__(self) -> None:
        self.vao.release()

    def _update_attributes(self) -> None:
        texture_id: int = 0

        for key, value in self.attributes.items():
            if type(value) == Texture:
                value.use(texture_id)
                self.program[key] = texture_id
                texture_id += 1

            elif type(value) == Framebuffer:
                value.color_attachments[0].use(texture_id)
                self.program[key] = texture_id
                texture_id += 1

            elif type(value) == DoubleFramebuffer:
                value.front.use(texture_id)
                self.program[key] = texture_id
                texture_id += 1

            elif type(value) in {tuple, list}:
                if len(value) == 0:
                    continue

                self.program[key] = value

            elif type(value) == Vector2:
                self.program[key] = value.x, value.y
            elif type(value) == Vector3:
                self.program[key] = value.x, value.y, value.z

            elif issubclass(type(value), Matrix2D) or issubclass(type(value), Matrix3D):
                self.program[key].write(data=value.as_array)

            else:
                self.program[key] = value

    def execute(self, reset_attributes: bool=True):
        self._update_attributes()

        self.ctx.enable(moderngl.BLEND)
        if self.viewport is not None:
            self.target.viewport = self.viewport

        if self.flip_fbo:
            self.target.flip()
        self.target.use()
        self.vao.render(moderngl.TRIANGLE_STRIP)

        self.ctx.disable(moderngl.BLEND)
        self.graphics.double_fbo.viewport = self.graphics.default_viewport

        if reset_attributes:
            self.reset_attributes()

    def reset_attributes(self) -> None:
        self.flip_fbo = True
        self.viewport = self.graphics.default_viewport
        self.target = self.graphics.double_fbo

    @property
    def as_string(self) -> str:
        return (f"program: {self.program}, "
                f"attributes: {self.attributes}, "
                f"target: {self.target}, "
                f"flip fbo: {self.flip_fbo}, "
                f"viewport: {self.viewport}")

    def __repr__(self):
        return self.as_string

    def __str__(self):
        return self.as_string
