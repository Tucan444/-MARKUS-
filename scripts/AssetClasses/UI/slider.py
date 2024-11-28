import math
import pygame, copy
from pygame import Surface, Vector2
from scripts.AssetClasses.UI.ui_element import UI_Element
from scripts.DataStructures.sorted_array import SortedArray
from scripts.GameTypes import (UISheetPosition, Resolution, Position,
                               DisplayPosition, HitboxType, SortableFunction,
                               Percentage, SF_key)


class Slider(UI_Element):
    def __init__(self, game: 'Game', ui_sheet: 'UI_Sheet', name: str,
                 position: UISheetPosition, layer: int, active: bool, input_wait: float,
                 min_value: float | int, max_value: float | int,
                 initial_value: float | int, whole_numbers: bool, enabled: bool,
                 knob_hitbox_type: HitboxType, slider_hitbox_type: HitboxType,
                 slider: Surface, slider_filled: Surface,
                 knob: Surface, knob_hover: Surface, knob_pressed: Surface,
                 knob_disabled: Surface):
        self.min_value: float | int = min_value if not whole_numbers else min_value // 1
        self.max_value: float | int = max_value if not whole_numbers else max_value // 1
        self.initial_value: float | int = initial_value if not whole_numbers else initial_value // 1
        self.value: float | int = self.initial_value
        self.range: float | int = self.max_value - self.min_value
        self.whole_numbers: bool = whole_numbers

        self.enabled: bool = enabled
        self.pressed: bool = False
        self.invoke_on_value_change: SortedArray = SortedArray(SortableFunction, key=SF_key)
        self.invoke_on_knob_press: SortedArray = SortedArray(SortableFunction, key=SF_key)
        self.invoke_on_knob_let: SortedArray = SortedArray(SortableFunction, key=SF_key)

        assert(initial_value >= min_value)
        assert(initial_value <= max_value)

        self.slider: Surface = slider
        self.slider_filled: Surface = slider_filled
        self._slider_processed: Surface = slider
        self.slider_processed_up_to_date: bool = False
        self.knob: Surface = knob
        self.knob_hover: Surface = knob_hover
        self.knob_pressed: Surface = knob_pressed
        self.knob_disabled: Surface = knob_disabled

        size: Resolution = (
            self.slider.get_width() - self.slider.get_height() + math.ceil(self.knob.get_width() * 0.5),
            self.knob.get_height()
        )

        # knob_hitbox_type gets passed as default -> self.hitbox_type
        super().__init__(game, ui_sheet, size, name, position, layer, active, input_wait, knob_hitbox_type)
        self.slider_hitbox_type: HitboxType = slider_hitbox_type

        assert (self.slider.get_size() == self.slider_filled.get_size())
        assert (self.knob.get_size() == self.knob_hover.get_size())
        assert (self.knob.get_size() == self.knob_pressed.get_size())
        assert (self.knob.get_size() == self.knob_disabled.get_size())
        assert (self.knob.get_height() >= self.slider.get_height())
        assert (self.knob.get_width() >= self.slider.get_height())
        if self.hitbox_type == HitboxType.CIRCLE:
            assert (self.knob.get_width() == self.knob.get_height())

        self.slider_size: Resolution = self.slider.get_size()
        self.knob_size: Resolution = self.knob.get_size()

        self.local_slider_position: Position = Vector2(0, 0)

        self.local_slider_position = Vector2(
            (self.knob_size[0] - self.slider_size[1]) * 0.5,
            (self.knob_size[1] - self.slider_size[1]) * 0.5
        )

        self.range_length: float = self.slider_size[0] - self.slider_size[1]

        self._mouse_left_press_funka: SortableFunction = (
            self.input_wait, f"slider: {self.name}", self.on_mouse_left_press, self.ui_sheet)
        self._mouse_left_let_funka: SortableFunction = (
            self.input_wait, f"slider: {self.name}", self.on_mouse_left_let, self.ui_sheet)

        self.game.inputs.on_mouse_left_press.add(self._mouse_left_press_funka)
        self.game.inputs.on_mouse_left_let.add(self._mouse_left_let_funka)

    @property
    def as_json(self) -> dict:
        json_form: dict = self.element_json

        image_names: dict[Surface, str] = self.game.assets.image_names

        json_form["type"] = "slider"
        json_form["enabled"] = self.enabled
        json_form["min value"] = self.min_value
        json_form["max value"] = self.max_value
        json_form["initial value"] = self.initial_value
        json_form["whole numbers"] = self.whole_numbers
        json_form["knob hitbox type"] = self.hitbox_type.value
        json_form["slider hitbox type"] = self.slider_hitbox_type.value
        json_form["slider"] = image_names[self.slider]
        json_form["slider filled"] = image_names[self.slider_filled]
        json_form["knob"] = image_names[self.knob]
        json_form["knob hover"] = image_names[self.knob_hover]
        json_form["knob pressed"] = image_names[self.knob_pressed]
        json_form["knob disabled"] = image_names[self.knob_disabled]

        return json_form

    @property
    def as_string(self) -> str:
        return (f"name: {self.name}, sheet name: {self.ui_sheet.name}, position: {self.position}, "
                f"enabled: {self.enabled}, pressed: {self.pressed}, progress: {self.progress}, "
                f"whole_numbers: {self.whole_numbers}, range: {self.range}, "
                f"active: {self.active}, layer: {self.layer}, hitbox type: {self.hitbox_type}")

    def __repr__(self):
        return self.as_string

    def __str__(self):
        return self.as_string

    @property
    def intersecting_mouse(self) -> bool:
        if not self.active:
            return False

        return self.knob_intersect_mouse or self.game.utilities.collide_point(
            self.slider_hitbox_type, self.slider_rect, self.game.mouse.position
        )

    @property
    def slider_rect(self) -> pygame.Rect:
        return pygame.Rect(*self.slider_blit_position, *self.slider_size)

    # returns values in range [0, 1]
    @property
    def progress(self) -> Percentage:
        return (self.value - self.min_value) / self.range

    @property
    def cutoff(self) -> float:
        return (self.slider_size[1] * 0.5) + (self.progress * self.range_length)

    @property
    def knob_blit_position(self) -> DisplayPosition:
        blit_position: DisplayPosition = Vector2(self.progress * self.range_length, 0)
        blit_position += self.position

        return self.ui_sheet.position_sheet_to_display(blit_position)

    @property
    def slider_blit_position(self) -> DisplayPosition:
        blit_position: DisplayPosition = self.local_slider_position + self.position
        return self.ui_sheet.position_sheet_to_display(blit_position)

    @property
    def knob_rect(self) -> pygame.Rect:
        return pygame.Rect(*self.knob_blit_position, *self.knob_size)

    @property
    def knob_intersect_mouse(self) -> bool:
        if not self.active:
            return False

        return self.game.utilities.collide_point(
            self.hitbox_type, self.knob_rect, self.game.mouse.position
        )

    @property
    def knob_hover_mouse(self) -> bool:
        return self.knob_intersect_mouse and (self == self.ui_sheet.top_element)

    @property
    def slider_processed(self) -> pygame.Surface:
        if self.slider_processed_up_to_date:
            return self._slider_processed

        int_cutoff: int = int(self.cutoff)

        filled: Surface = Surface((int_cutoff, self.slider_size[1]))
        filled.blit(self.slider_filled, (0, 0))

        non_filled: Surface = Surface((self.slider_size[0] - int_cutoff, self.slider_size[1]))
        non_filled.blit(self.slider, (-int_cutoff, 0))

        self._slider_processed = Surface(self.slider_size)
        self._slider_processed.blit(filled, (0, 0))
        self._slider_processed.blit(non_filled, (int_cutoff, 0))

        self.slider_processed_up_to_date = True

        return self._slider_processed

    def on_mouse_left_press(self) -> None:
        if not self.active or not self.enabled:
            return

        if self.knob_hover_mouse:
            self.pressed = True
            self.game.utilities.call_functions(self.invoke_on_knob_press, (self,))

    def on_mouse_left_let(self) -> None:
        if not self.active or not self.enabled:
            return

        if self.pressed:
            self.game.utilities.call_functions(self.invoke_on_knob_let, (self,))

        self.pressed = False

    def update_value(self) -> None:
        original_value: float | int = self.value

        mouse_pos_local: UISheetPosition = self.game.mouse.position - self.display_position
        x_progress = mouse_pos_local[0] - self.local_slider_position[0] - (self.slider_size[1] * 0.5)
        x_progress /= self.range_length
        x_progress = max(0, min(1, x_progress))

        self.value = self.min_value + (self.range * x_progress)
        self.value = self.value // 1 if self.whole_numbers else self.value

        if original_value != self.value:
            self.slider_processed_up_to_date = False
            self.game.utilities.call_functions(self.invoke_on_value_change, (self,))

    def clear_callbacks(self) -> None:
        self.invoke_on_value_change.clear()
        self.invoke_on_knob_let.clear()
        self.invoke_on_knob_press.clear()

    def detach(self) -> None:
        self.clear_callbacks()
        self.ui_sheet.remove_element(self)
        self.game.inputs.on_mouse_left_press.remove(self._mouse_left_press_funka)
        self.game.inputs.on_mouse_left_let.remove(self._mouse_left_let_funka)

    def blit(self):
        self.game.window.display.blit(self.slider_processed, self.slider_blit_position)

        knob_blit_image: Surface = self.knob
        if not self.enabled:
            knob_blit_image = self.knob_disabled
        elif self.pressed:
            knob_blit_image = self.knob_pressed
        elif self.knob_hover_mouse:
            knob_blit_image = self.knob_hover

        self.game.window.display.blit(knob_blit_image, self.knob_blit_position)

        if self.pressed:
            self.update_value()
