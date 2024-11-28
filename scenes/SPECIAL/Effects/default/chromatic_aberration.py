from scenes.SPECIAL.Effects.Effect import Effect
from scripts.GameTypes import DisplayPosition, UV_Position
from scripts.Utilities.Graphics.double_framebuffer import DoubleFramebuffer
from scripts.Utilities.Graphics.frag import Frag


class ChromaticAberration(Effect):
    def __init__(self, frag: Frag, focal_point: DisplayPosition=None, power: float=1,
                 red_offset: float=-1, green_offset: float=1, blue_offset: float=0):
        super().__init__(frag)

        self.tex: DoubleFramebuffer = self.graphics.double_fbo
        self.focal_point: DisplayPosition = focal_point \
            if focal_point is not None else self.game.window.display_center

        self.power: float = power
        self.red_offset: float = red_offset
        self.green_offset: float = green_offset
        self.blue_offset: float = blue_offset

    @property
    def clone(self) -> 'ChromaticAberration':
        return ChromaticAberration(self.frag)

    @property
    def red_offset_uv(self) -> float:
        return self.red_offset / self.game.window.display_size[1]

    @property
    def green_offset_uv(self) -> float:
        return self.green_offset / self.game.window.display_size[1]

    @property
    def blue_offset_uv(self) -> float:
        return self.blue_offset / self.game.window.display_size[1]

    @property
    def focal_point_uv_position(self) -> UV_Position:
        uv_position: UV_Position = self.graphics.position_display_to_uv(self.focal_point)
        uv_position.y = 1 - uv_position.y
        return uv_position

    def _update_frag(self) -> None:
        self.frag.attributes = {
            "tex": self.tex,
            "focal_point": self.focal_point_uv_position,
            "red_offset": self.red_offset_uv * self.power,
            "green_offset": self.green_offset_uv * self.power,
            "blue_offset": self.blue_offset_uv * self.power
        }
