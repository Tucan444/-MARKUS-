import os
import time
from array import array

import moderngl
from moderngl import Texture, Program, Buffer, VertexArray, Framebuffer, Context
from pygame import Surface, Vector2

from scenes.SPECIAL.Effects.Effect import Effect
from scripts.DataStructures.sorted_array import SortedArray
from scripts.GameTypes import Success, ColorNormalized, UV_Position, DisplayPosition, ClipPosition, Viewport, Vector, \
    UV_Vector, Resolution, UVN_Position
from scripts.Utilities.Graphics.double_framebuffer import DoubleFramebuffer

from scripts.Utilities.Graphics.frag import Frag
from scripts.Utilities.Graphics.graphics_command import GraphicsCommand
from scripts.Utilities.Graphics.kernel import Kernel


class Graphics:
    def __init__(self, game: 'Game'):
        self.game: 'Game' = game

        if not self.opengl:
            return

        self.ctx: Context = moderngl.create_context()
        self.double_fbo: DoubleFramebuffer = None

        self.programs: dict[str, Program] = {}
        self.textures: dict[str, Texture] = {}
        self.temp_textures: list[Texture] = []
        self.frags: dict[str, Frag] = {}
        self.effects: dict[str, Effect] = {}
        self.command_queue: list[GraphicsCommand] = []

        self.quad_vertices: Buffer = self.ctx.buffer(data=array('f', [
            -1.0, 1.0,
            1.0, 1.0,
            -1.0, -1.0,
            1.0, -1.0
        ]))
        self.blit_uvs: Buffer = self.ctx.buffer(data=array('f', [
            0.0, 0.0,
            1.0, 0.0,
            0.0, 1.0,
            1.0, 1.0
        ]))
        self.effect_uvs: Buffer = self.ctx.buffer(data=array('f', [
            0.0, 1.0,
            1.0, 1.0,
            0.0, 0.0,
            1.0, 0.0
        ]))

        self.vertex_shader: str = ''
        with open(f"{self.game.utilities.DEFAULT_SHADER_PATH}/main.vert") as f:
            self.vertex_shader = f.read()

        self._load_programs()

        self.blit_vao: VertexArray = self.ctx.vertex_array(self.programs["main"], [
            (self.quad_vertices, '2f', 'position'),
            (self.blit_uvs, '2f', 'texcoord')
        ])
        self.effect_vao: VertexArray = self.ctx.vertex_array(self.programs["main"], [
            (self.quad_vertices, '2f', 'position'),
            (self.effect_uvs, '2f', 'texcoord')
        ])

        self.UV_PIXEL_SIZE: UV_Vector = self.position_display_to_uv(Vector2(1, 1))
        self.kernel_black: Texture = None
        self.kernel_white: Texture = None

        self._load_black_white()

    def init(self) -> None:
        if not self.opengl:
            return

        self.double_fbo = self.get_display_double_framebuffer()

        self._load_frags()
        self._load_effects()

    def update(self) -> None:
        if not self.opengl:
            return

        self._handle_command_queue()
        self._blit_fbo_to_display()
        self._release_temp_textures()

    def end(self) -> None:
        if not self.opengl:
            return

    def _handle_command_queue(self) -> None:
        self.command_queue.sort(key=lambda x: x.order)

        for command in self.command_queue:
            command.execute()

        self.command_queue = []

    def _blit_fbo_to_display(self) -> None:
        self.ctx.screen.use()

        self.double_fbo.front.use(0)
        self.programs["main"]["tex"] = 0
        self.programs["main"]["position"] = 0, 0
        self.programs["main"]["alpha"] = 1
        self.ctx.screen.viewport = (*self.game.window.dp, *self.game.window.blit_size)
        self.effect_vao.render(moderngl.TRIANGLE_STRIP)

        self.double_fbo.use()

    def _release_temp_textures(self) -> None:
        for texture in self.temp_textures:
            texture.release()

        self.temp_textures = []

    @property
    def opengl(self) -> bool:
        return self.game.window.opengl

    @property
    def default_viewport(self) -> Viewport:
        return (
            0, 0, self.game.window.display_size[0], self.game.window.display_size[1]
        )

    def get_display_double_framebuffer(self, use_floats: bool=False) -> DoubleFramebuffer:
        return DoubleFramebuffer(self.game,
             self.get_texture(self.game.window.display_size, repeat=True, use_floats=use_floats),
             self.get_texture(self.game.window.display_size, repeat=True, use_floats=use_floats))

    def _load_black_white(self) -> None:
        black: Surface = Surface((1, 1))
        black.fill(Kernel.ZERO_TUPLE)
        self.black = self.surface_to_texture(black, True, BGRA=False)

        white: Surface = Surface((1, 1))
        white.fill(Kernel.ONE_TUPLE)
        self.white = self.surface_to_texture(white, True, BGRA=False)

    def _load_program(self, filename: str) -> Success:
        name: str = filename.split("/")[-1][:-5]
        if name in self.programs:
            return False

        path: str = f"{self.game.utilities.DEFAULT_SHADER_PATH}/{filename}"

        with open(path) as f:
            fragment_shader: str = f.read()

        program: Program = self.ctx.program(vertex_shader=self.vertex_shader,
                                            fragment_shader=fragment_shader)

        self.programs[name] = program
        return True

    def _load_programs(self) -> None:
        dirs_to_do: set[str] = set()

        for file in os.listdir(self.game.utilities.DEFAULT_SHADER_PATH):
            if "__" in file or file[-5:] == ".vert":
                continue

            if file[-5:] == ".frag":
                self._load_program(file)
            else:
                dirs_to_do.add(file)

        to_clear: list[str] = []
        to_add: list[str] = []
        while dirs_to_do:
            to_clear += dirs_to_do

            for dir_ in dirs_to_do:
                for file in os.listdir(f"{self.game.utilities.DEFAULT_SHADER_PATH}/{dir_}"):
                    if "__" in file or file[-5:] == ".vert":
                        continue

                    if file[-5:] == ".frag":
                        self._load_program(f"{dir_}/{file}")
                    else:
                        to_add.append(f"{dir_}/{file}")

            for item in to_clear:
                dirs_to_do.remove(item)

            for item in to_add:
                dirs_to_do.add(item)

            to_clear = []
            to_add = []

    def _load_frags(self) -> None:
        for name, program in self.programs.items():
            self.frags[name] = Frag(self.game, program)

    def _load_effects(self) -> None:
        effects_scene_name: str = self.game.scene_manager.EFFECTS
        effects_scene: 'Scene' = self.game.scene_manager.scenes[effects_scene_name]

        for name, effect in effects_scene.classes.items():
            wrong_name: bool = name == "Effect"
            not_effect: bool = not issubclass(effect, Effect)

            if wrong_name or not_effect:
                continue

            name = self.game.utilities.camel_to_snake_case(name)
            no_matching_frag: bool = name not in self.frags

            if no_matching_frag:
                self.effects[name] = effect(self.frags["main"])
            else:
                self.effects[name] = effect(self.frags[name])

        for effect in self.effects.values():
            effect.init()

    def surface_to_texture(self, surface: Surface, repeat: bool=False, BGRA: bool=True) -> Texture:
        texture = self.ctx.texture(surface.get_size(), 4)
        texture.filter = (moderngl.NEAREST, moderngl.NEAREST)
        if BGRA:
            texture.swizzle = 'BGRA' # Red -> Blue, Blue -> Red
        texture.repeat_x = repeat
        texture.repeat_y = repeat
        texture.write(surface.get_view('1'))
        return texture

    def get_texture(self, size: Resolution, repeat: bool=False, use_floats: bool=False):
        data_type: str = 'f2' if use_floats else 'f1'
        texture = self.ctx.texture(size, 4, dtype=data_type)
        texture.filter = (moderngl.NEAREST, moderngl.NEAREST)
        texture.repeat_x = repeat
        texture.repeat_y = repeat
        return texture

    def clear(self, screen: bool=True, framebuffer: bool=True) -> None:
        clear_color: ColorNormalized = self.game.window.clear_color
        clear_color = (clear_color[0] / 255, clear_color[1] / 255, clear_color[2] / 255)

        if screen:
            self.ctx.clear(*clear_color)
        if framebuffer:
            self.double_fbo.clear(*clear_color)

    def blit_surface(self, position: UV_Position, surface: Surface, alpha: float=1, equation=moderngl.FUNC_ADD,
                     funcs=(moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA)) -> None:
        texture: Texture = self.surface_to_texture(surface)
        self.blit_texture(position, texture, alpha, equation, funcs, True)
        texture.release()

    def blit_texture(self, position: UV_Position, texture: Texture, alpha: float=1, equation=moderngl.FUNC_ADD,
                     funcs=(moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA), use_blit_vao: bool=False) -> None:
        self.ctx.enable(moderngl.BLEND)
        self.ctx.blend_equation = equation
        self.ctx.blend_func = funcs[0], funcs[1]

        texture.use(0)
        self.programs["main"]["tex"] = 0
        self.programs["main"]["position"] = position.x, position.y
        self.programs["main"]["alpha"] = alpha

        if use_blit_vao:
            self.blit_vao.render(moderngl.TRIANGLE_STRIP)
        else:
            self.effect_vao.render(moderngl.TRIANGLE_STRIP)

        self.ctx.disable(moderngl.BLEND)
        self.ctx.blend_equation = moderngl.FUNC_ADD
        self.ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA

    def position_display_to_uv(self, position: DisplayPosition) -> UV_Position:
        return Vector2(
            position.x / self.game.window.display_size[0],
            position.y / self.game.window.display_size[1]
        )

    def position_uv_to_display(self, position: UV_Position) -> DisplayPosition:
        return Vector2(
            position.x * self.game.window.display_size[0],
            position.y * self.game.window.display_size[1]
        )

    def position_uv_to_uvn(self, position: UV_Position) -> UVN_Position:
        return Vector2((position.x - 0.5) * self.game.window.aspect_ratio, position.y - 0.5)

    def position_uvn_to_uv(self, position: UVN_Position) -> UV_Position:
        return Vector2(position.x * self.game.window.aspect_ratio_inverse, position.y) + Vector2(0.5, 0.5)

    def position_display_to_uvn(self, position: DisplayPosition) -> UVN_Position:
        return self.position_uv_to_uvn(self.position_display_to_uv(position))

    def position_uvn_to_display(self, position: UVN_Position) -> DisplayPosition:
        return self.position_uv_to_display(self.position_uvn_to_uv(position))

    @staticmethod
    def position_uv_to_clip(position: UV_Position) -> ClipPosition:
        return (position - Vector2(0.5, 0.5)) * 2

    @staticmethod
    def position_clip_to_uv(position: ClipPosition) -> UV_Position:
        return (position * 0.5) + Vector2(0.5, 0.5)

    def position_display_to_clip(self, position: DisplayPosition) -> ClipPosition:
        return self.position_uv_to_clip(self.position_display_to_uv(position))

    def position_clip_to_display(self, position: ClipPosition) -> DisplayPosition:
        return self.position_clip_to_uv(self.position_uv_to_display(position))

    @property
    def as_string(self) -> str:
        return (f"graphics, "
                f"programs: {len(self.programs)}, "
                f"frags: {len(self.frags)}, "
                f"effects: {len(self.effects)}"
                f"textures: {len(self.textures)}, "
                f"temp textures: {len(self.temp_textures)}, "
                f"commands in queue: {len(self.command_queue)}")

    def __repr__(self):
        return self.as_string

    def __str__(self):
        return self.as_string
