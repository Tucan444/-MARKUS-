from scripts.GameTypes import ColorNormalized, Color
from scripts.Utilities.Graphics.effect_area import EffectArea


class LightGPU:
    def __init__(self, effect_area: EffectArea, light_color: Color, light_intensity: float):
        self.effect_area: EffectArea = effect_area
        self.light_color: Color = light_color
        self.light_intensity: float = light_intensity

    @property
    def shader_light_color(self) -> ColorNormalized:
        multiplier: float = self.light_intensity / 255.

        return (self.light_color[0] * multiplier,
                self.light_color[1] * multiplier,
                self.light_color[2] * multiplier)

    @property
    def clone(self) -> 'LightGPU':
        return LightGPU(self.effect_area.clone, (*self.light_color,), self.light_intensity)
