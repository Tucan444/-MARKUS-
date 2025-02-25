from scenes.SPECIAL.Effects.Effect import Effect
from scenes.SPECIAL.Effects.default.texture_calculator import TextureCalculator
from scripts.GameTypes import ColorNormalized, Percentage, OperationType, FloatDoubleFBO
from scripts.Utilities.Graphics.double_framebuffer import DoubleFramebuffer
from scripts.Utilities.Graphics.effect_area import EffectArea
from scripts.Utilities.Graphics.frag import Frag
from scripts.Utilities.Graphics.kernel import Kernel
from scripts.Utilities.Graphics.light_gpu import LightGPU


class Lighting(Effect):
    def __init__(self, frag: Frag, ambient_color: ColorNormalized=(0., 0., 0.),
                 calculation_target: FloatDoubleFBO=None):
        super().__init__(frag)

        self.tex: DoubleFramebuffer = self.graphics.double_fbo
        self.calculation_target: FloatDoubleFBO = calculation_target
        self.texture_calculator: 'TextureCalculator' = None

        self.ambient_color: ColorNormalized = ambient_color
        self.lights: set[LightGPU] = set()

    def init(self) -> None:
        self.texture_calculator = self.graphics.effects["texture_calculator"].clone

    @property
    def clone(self) -> 'Lighting':
        lighting = Lighting(self.frag, self.ambient_color, self.calculation_target)
        lighting.lights = {
            light.clone for light in self.lights
        }

        lighting.init()
        return lighting

    def get_light_presences(self) -> tuple[bool, list[tuple[LightGPU, bool]]]:
        light_is_present: bool = False
        light_presences: list[tuple[LightGPU, bool]] = []

        for light in self.lights:
            presence: bool = False
            effect_area: EffectArea = light.effect_area

            if not effect_area.hill_of_peace and self.game.window.display_rect.colliderect(effect_area.display_rect):
                presence = True
                light_is_present = True

            if effect_area.hill_of_peace and not effect_area.display_rect.contains(self.game.window.display_rect):
                presence = True
                light_is_present = True

            light_presences.append((light, presence))

        return light_is_present, light_presences

    def _update_frag(self) -> None:
        self.calculation_target.fbo.clear(*self.ambient_color, 1.0)

        self.texture_calculator.tex_a = self.calculation_target.front
        self.texture_calculator.tex_b = self.frag.target.front
        self.texture_calculator.target = self.frag.target
        self.texture_calculator.operation = OperationType.MULTIPLY

    def _execute_frag(self) -> None:
        light_is_present, light_presences = self.get_light_presences()

        if not light_is_present:
            self.texture_calculator.execute()
            self.frag.reset_attributes()
            return

        for light, presence in light_presences:
            if not presence:
                continue

            effect_area: EffectArea = light.effect_area

            attributes: dict = effect_area.shader_attributes
            attributes["aspect_ratio"] = self.game.window.aspect_ratio

            attributes["tex_light"] = self.calculation_target.front
            attributes["light_color"] = (*light.shader_light_color, 1.0)

            self.frag.attributes = attributes

            self.frag.target = self.calculation_target
            self.frag.flip_fbo = False
            self.frag.execute()

        self.texture_calculator.execute()
