import pygame.draw
from pygame import Vector2

from scenes.SPECIAL.Effects.default.pixel_transform import PixelTransform
from scenes.SPECIAL.Effects.default.positioned_effect import PositionedEffect
from scenes.scene_behaviour import SceneBehaviour
from scripts.AssetClasses.UI.slider import Slider
from scripts.AssetClasses.UI.text import Text
from scripts.GameTypes import CommandType, DisplayPosition
from scripts.Utilities.Graphics.double_framebuffer import DoubleFramebuffer
from scripts.Utilities.Graphics.effect_area import EffectArea
from scripts.Utilities.Graphics.graphics_command import GraphicsCommand


class EffectEditor(SceneBehaviour):
    SCALE=1
    FS_SCALE=1
    DRAW_SCREEN_PREVIEW=True
    PRINT_TO_FILE=True
    FILEPATH="area_effects.txt"

    def __init__(self, game, scene, active, order):
        super().__init__(game, scene, active, order)

        self.tilemap_name = "boilmap"
        self.ui_sheet_name = "area effect editor ui sheet"

        self.tilemap = None
        self.ui_sheet = None

        self.movement: 'EditorMovement' = None

        self.inv_effect: PixelTransform = None
        self.inv_positioned: PositionedEffect = None
        self.positioning_fbo: DoubleFramebuffer = None

        self.inv_command: GraphicsCommand = None

        self.area_effects: list[EffectArea] = []

        self.selecting: bool = False
        self.selected_index: int = -1
        self.single_point_mode: bool = False

        self.placing_point: bool = False
        self.in_world: bool = True
        self.hill_of_peace: bool = False

        self.first_point: Vector2 | None = None
        self.radius: Slider = None
        self.falloff: Slider = None
        self.falloff_speed: Slider = None

        self.save_as_light: bool = False

        self.screen_preview = pygame.Surface(self.game.window.display_size)
        self.screen_preview.fill((100, 100, 250))
        self.screen_preview.set_alpha(60)

        self.game.inputs.on_mouse_left_press.add((-5, "effect_editor_press", self.on_mouse_callback, self.scene))
        self.game.inputs.on_d_press.add((-50, "delete effect area", self.delete_selected, self.scene))
        self.game.inputs.on_s_press.add((-50, "print effect areas", self.print_areas, self.scene))

    def init(self):
        self.tilemap = self.game.assets.tilemaps[self.tilemap_name].clone
        self.ui_sheet = self.game.assets.ui_sheets[self.ui_sheet_name].clone
        self.ui_sheet.active = True

        self.radius = self.ui_sheet.elements["RadiusSlider"]
        self.falloff = self.ui_sheet.elements["FalloffSlider"]
        self.falloff_speed = self.ui_sheet.elements["FalloffSpeedSlider"]

        self.movement = self.scene.classes["EditorMovement"](self)

        self._configure_effects()
        self._add_sheet_callbacks()

    def _configure_effects(self) -> None:
        self.inv_effect = self.game.graphics.effects["pixel_transform"].clone
        self.inv_effect.invert_color = 1

        self.positioning_fbo = self.game.graphics.get_display_double_framebuffer()
        self.inv_positioned = self.game.graphics.effects["positioned_effect"].clone
        self.inv_positioned.calculation_target = self.positioning_fbo
        self.inv_positioned.effect = self.inv_effect

        for area in self.area_effects:
            self.inv_positioned.effect_areas.add(area)

        self.inv_command = GraphicsCommand(self.game, 18, CommandType.EFFECT, effect=self.inv_positioned)

    def _add_sheet_callbacks(self) -> None:
        self.ui_sheet.elements["NEW"].invoke_on_press.add((0, "toggle new", self.on_new_press))
        self.ui_sheet.elements["POINT"].invoke_on_press.add((0, "toggle point", self.on_point_press))
        self.ui_sheet.elements["IN WORLD"].invoke_on_press.add((0, "toggle in world", self.on_in_world_press))
        self.ui_sheet.elements["HILL OF PEACE"].invoke_on_press.add((0, "toggle point", self.on_hill_press))

        self.radius.invoke_on_value_change.add((0, "radius change", self.on_radius_change))
        self.falloff.invoke_on_value_change.add((0, "falloff change", self.on_falloff_change))
        self.falloff_speed.invoke_on_value_change.add((0, "falloff speed change", self.on_falloff_speed_change))

        self.ui_sheet.elements["LIGHT"].invoke_on_press.add((0, "toggle save as light", self.on_light_press))

    def update(self):
        self.movement.update()

        self.tilemap.blit()
        self.ui_sheet.blit()

        self.ui_sheet.elements["COUNT"].text = str(len(self.area_effects))
        self.ui_sheet.elements["SELECTED"].text = str(self.selected_index + 1)

        if self.first_point is not None:
            blit_pos: DisplayPosition = Vector2(*self.first_point)
            if self.in_world:
                blit_pos = self.game.camera.position_world_to_display(self.first_point)

            rect = pygame.Rect(blit_pos, self.game.mouse.position - blit_pos)
            rect.normalize()

            pygame.draw.rect(self.game.window.display, (200, 200, 255), rect, 2)
            pygame.draw.circle(self.game.window.display, (150, 150, 255), blit_pos, 10)

        if self.DRAW_SCREEN_PREVIEW:
            blit_pos = self.game.camera.position_world_to_display(Vector2(0, 0))
            self.game.window.display.blit(self.screen_preview, blit_pos)

        self.game.graphics.command_queue.append(self.inv_command)

    def end(self):
        pass

    def on_new_press(self, text: Text) -> None:
        self.selecting = not self.selecting
        text.color_idle = (120, 120, 120) if self.selecting else (200, 200, 255)

    def on_point_press(self, text: Text) -> None:
        self.placing_point = not self.placing_point
        text.color_idle = (120, 120, 120) if not self.placing_point else (200, 200, 255)


    def on_in_world_press(self, text: Text) -> None:
        self.in_world = not self.in_world
        text.color_idle = (120, 120, 120) if not self.in_world else (200, 200, 255)

        if self.selected_index >= 0:
            self.area_effects[self.selected_index].in_world = self.in_world


    def on_hill_press(self, text: Text) -> None:
        self.hill_of_peace = not self.hill_of_peace
        text.color_idle = (120, 120, 120) if not self.hill_of_peace else (200, 200, 255)

        if self.selected_index >= 0:
            self.area_effects[self.selected_index].hill_of_peace = self.hill_of_peace

    def on_radius_change(self, _) -> None:
        if self.selected_index >= 0:
            self.area_effects[self.selected_index].radius = self.radius.value * self.SCALE

    def on_falloff_change(self, _) -> None:
        if self.selected_index >= 0:
            self.area_effects[self.selected_index].falloff = self.falloff.value * self.SCALE

    def on_falloff_speed_change(self, _) -> None:
        if self.selected_index >= 0:
            self.area_effects[self.selected_index].falloff_speed = self.falloff_speed.value * self.FS_SCALE

    def on_light_press(self, text: Text) -> None:
        self.save_as_light = not self.save_as_light
        text.color_idle = (120, 120, 120) if not self.save_as_light else (200, 200, 255)

    @property
    def placing_pos(self) -> Vector2:
        if self.in_world:
            return self.game.mouse.world_position
        else:
            return self.game.mouse.position

    def on_mouse_callback(self) -> None:
        if self.ui_sheet.intersecting_mouse:
            return

        if self.selecting:
            self.select()
            return

        if self.placing_point:
            self.create_new_area_effect(self.placing_pos, Vector2(0, 0))
            self.first_point = None
        else:
            if self.first_point is not None:
                self.create_new_area_effect(self.first_point, self.placing_pos - self.first_point)
                self.first_point = None
            else:
                self.first_point = self.placing_pos

    def select(self) -> None:
        mouse_pos = self.game.mouse.position
        pairs = []

        for i, area in enumerate(self.area_effects):
            d = area.sdf_display(mouse_pos)
            pairs.append((d, i))

        pairs.sort(key=lambda x: x[0])

        for d, i in pairs:
            if i == self.selected_index:
                continue

            if d == 1:
                self.selected_index = -1
                break

            self.selected_index = i
            selected_area: EffectArea = self.area_effects[self.selected_index]

            if selected_area.in_world != self.in_world:
                self.on_in_world_press(self.ui_sheet.elements["IN WORLD"])

            if selected_area.hill_of_peace != self.hill_of_peace:
                self.on_hill_press(self.ui_sheet.elements["HILL OF PEACE"])

            self.radius.value = selected_area.radius
            self.falloff.value = selected_area.falloff
            self.falloff_speed.value = selected_area.falloff_speed

            break


    def create_new_area_effect(self, p1: Vector2, p2: Vector2) -> None:
        if p2.x < 0:
            p1.x += p2.x
            p2.x *= -1

        if p2.y < 0:
            p1.y += p2.y
            p2.y *= -1

        new_area: EffectArea = EffectArea(
            self.game, p1, p2,
            self.radius.value * self.SCALE,
            self.falloff.value * self.SCALE,
            self.falloff_speed.value * self.FS_SCALE,
            self.in_world, self.hill_of_peace)

        self.inv_positioned.effect_areas.add(new_area)
        self.area_effects.append(new_area)
        self.selected_index = len(self.area_effects) - 1

    def delete_selected(self) -> None:
        if self.selected_index < 0:
            return

        to_delete: EffectArea = self.area_effects[self.selected_index]
        self.area_effects.remove(to_delete)
        self.inv_positioned.effect_areas.remove(to_delete)

        self.selected_index = -1

    def print_areas(self) -> None:
        text = f"[\n"

        for area in self.area_effects:
            if self.save_as_light:
                text += "LightGPU("

            text += (f"EffectArea("
                     f"self.game, Vector2({area.position.x}, {area.position.y}),"
                     f"Vector2({area.size.x}, {area.size.y}),"
                     f"{area.radius}, {area.falloff}, {area.falloff_speed},"
                     f"{area.in_world}, {area.hill_of_peace}),\n")

            if self.save_as_light:
                text += "(200, 200, 200), 1.0),\n"

        text = f"{text[:-2]}]\n"

        if self.PRINT_TO_FILE:
            with open(self.FILEPATH, 'w') as f:
                f.write(text)

            print(f"effect areas saved to {self.FILEPATH}")
        else:
            print(text)
