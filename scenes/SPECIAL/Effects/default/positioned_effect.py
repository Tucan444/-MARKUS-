from pygame import Vector2

from scenes.SPECIAL.Effects.Effect import Effect
from scripts.Utilities.Graphics.double_framebuffer import DoubleFramebuffer
from scripts.Utilities.Graphics.effect_area import EffectArea
from scripts.Utilities.Graphics.frag import Frag


# CODE YELLOW, expects input to be from its target and output of effect to be on the other side of its target
class PositionedEffect(Effect):
    def __init__(self, frag: Frag, effect: Effect=None, effect_areas: set[EffectArea]=None,
                 calculation_target: DoubleFramebuffer=None):
        super().__init__(frag)

        self.effect: Effect = effect
        self.effect_areas: set[EffectArea] = effect_areas if effect_areas is not None else set()
        self.calculation_target: DoubleFramebuffer = calculation_target

        self._persistent_target: DoubleFramebuffer = None

    @property
    def clone(self) -> 'PositionedEffect':
        return PositionedEffect(self.frag, self.effect, self.effect_areas, self.calculation_target)

    def get_area_presences(self) -> tuple[bool, list[tuple[EffectArea, bool]]]:
        area_is_present: bool = False
        area_presences: list[tuple[EffectArea, bool]] = []

        for effect_area in self.effect_areas:
            presence: bool = False

            if not effect_area.hill_of_peace and self.game.window.display_rect.colliderect(effect_area.display_rect):
                presence = True
                area_is_present = True

            if effect_area.hill_of_peace and not effect_area.display_rect.contains(self.game.window.display_rect):
                presence = True
                area_is_present = True

            area_presences.append((effect_area, presence))

        return area_is_present, area_presences

    def _configure_frag(self) -> None:
        assert self.effect is not None

        self._persistent_target = self.frag.target
        self.effect.frag.target = self._persistent_target
        self.effect.tex = self._persistent_target

    def _execute_frag(self) -> None:
        area_is_present, area_presences = self.get_area_presences()

        if not area_is_present:
            self.effect.frag.reset_attributes()
            self.frag.reset_attributes()
            return

        self.calculation_target.use()
        self.graphics.blit_texture(Vector2(), self._persistent_target.front)

        self.effect.execute()

        first_area: bool = True
        self._persistent_target.flip()
        for effect_area, presence in area_presences:
            if not presence:
                continue

            attributes: dict = effect_area.shader_attributes
            attributes["aspect_ratio"] = self.game.window.aspect_ratio

            if first_area:
                attributes["tex_source"] = self.calculation_target.front
                first_area = False
            else:
                attributes["tex_source"] = self._persistent_target.front
            attributes["tex_dest"] = self._persistent_target.back

            self.frag.attributes = attributes

            self.frag.target = self._persistent_target
            self.frag.flip_fbo = False
            self.frag.execute()
