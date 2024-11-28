from pygame import Vector2

from scenes.SPECIAL.Effects.Effect import Effect
from scripts.GameTypes import ColorNormalized, Percentage, Scaling, DisplayVector, Angle, HyperAngle, Shear, \
    UV_Position, DisplayPosition
from scripts.Utilities.Flow.timeline import Timeline
from scripts.Utilities.Graphics.double_framebuffer import DoubleFramebuffer
from scripts.Utilities.Graphics.frag import Frag
from scripts.DataStructures.matrices import Matrix2D


class Wavy(Effect):
    def __init__(self, frag: Frag, timeline: Timeline=None, x_sine: float=0, x_sine_frequency: float=1,
                 y_sine: float=0, y_sine_frequency: float=1, twist_position: DisplayPosition=None,
                 twist: Angle=0, twist_falloff: float=10):
        super().__init__(frag)

        self.tex: DoubleFramebuffer = self.graphics.double_fbo
        self.timeline: Timeline = timeline if timeline is not None else Timeline.blank(self.game)

        self.x_sine: float = x_sine
        self.x_sine_frequency: float = x_sine_frequency
        self.y_sine: float = y_sine
        self.y_sine_frequency: float = y_sine_frequency

        self.twist_position: DisplayPosition = twist_position
        if self.twist_position is None:
            self.twist_position = self.game.window.display_center

        self.twist: Angle = twist
        self.twist_falloff: float = twist_falloff

    @property
    def clone(self) -> 'Wavy':
        return Wavy(self.frag, self.timeline, self.x_sine, self.x_sine_frequency,
                    self.y_sine, self.y_sine_frequency, self.twist_position, self.twist, self.twist_falloff)

    @property
    def twist_uv_position(self) -> UV_Position:
        uv_position: UV_Position = self.graphics.position_display_to_uv(self.twist_position)
        uv_position.y = 1 - uv_position.y
        return uv_position

    def _update_frag(self) -> None:
        self.frag.attributes = {
            "tex": self.tex,
            "time": self.timeline.local_timeline_duration,
            "x_sine": self.x_sine,
            "x_sine_frequency": self.x_sine_frequency,
            "y_sine": self.y_sine,
            "y_sine_frequency": self.y_sine_frequency,
            "twist_position": self.twist_uv_position,
            "twist": self.twist,
            "twist_falloff": self.twist_falloff,
            "aspect_ratio": self.game.window.aspect_ratio,
            "aspect_ratio_inverse": self.game.window.aspect_ratio_inverse
        }
