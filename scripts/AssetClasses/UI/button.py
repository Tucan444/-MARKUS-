from pygame import Surface

from scripts.AssetClasses.UI.ui_element import UI_Element
from scripts.DataStructures.sorted_array import SortedArray
from scripts.GameTypes import UISheetPosition, Resolution, HitboxType, SortableFunction, SF_key


class Button(UI_Element):
    def __init__(self, game: 'Game', ui_sheet: 'UI_Sheet', name: str,
                 position: UISheetPosition, layer: int, active: bool, input_wait: float,
                 enabled: bool, hitbox_type: HitboxType,
                 idle_image: Surface, hover_image: Surface,
                 pressed_image: Surface, disabled_image: Surface):
        super().__init__(game, ui_sheet, idle_image.get_size(), name, position, layer, active,
                         input_wait, hitbox_type)
        self.enabled: bool = enabled
        self.pressed: bool = False
        self.invoke_on_press: SortedArray = SortedArray(SortableFunction, key=SF_key)
        self.invoke_on_let: SortedArray = SortedArray(SortableFunction, key=SF_key)

        self.idle_image: Surface = idle_image
        self.hover_image: Surface = hover_image
        self.pressed_image: Surface = pressed_image
        self.disabled_image: Surface = disabled_image

        # size is size of self.idle_image
        assert(self.hover_image.get_size() == self.size)
        assert(self.pressed_image.get_size() == self.size)
        assert(self.disabled_image.get_size() == self.size)

        if self.hitbox_type == HitboxType.CIRCLE:
            assert(self.size[0] == self.size[1])

        self._mouse_left_press_funka: SortableFunction = (
            self.input_wait, f"button: {self.name}", self.on_mouse_left_press, self.ui_sheet)
        self._mouse_left_let_funka: SortableFunction = (
            self.input_wait, f"button: {self.name}", self.on_mouse_left_let, self.ui_sheet)

        self.game.inputs.on_mouse_left_press.add(self._mouse_left_press_funka)
        self.game.inputs.on_mouse_left_let.add(self._mouse_left_let_funka)

    @property
    def as_json(self) -> dict:
        json_form: dict = self.element_json

        image_names: dict[Surface, str] = self.game.assets.image_names

        json_form["type"] = "button"
        json_form["enabled"] = self.enabled
        json_form["idle image"] = image_names[self.idle_image]
        json_form["hover image"] = image_names[self.hover_image]
        json_form["pressed image"] = image_names[self.pressed_image]
        json_form["disabled image"] = image_names[self.disabled_image]

        return json_form

    @property
    def as_string(self) -> str:
        return (f"name: {self.name}, sheet name: {self.ui_sheet.name}, position: {self.position}, "
                f"enabled: {self.enabled}, pressed: {self.pressed}, "
                f"active: {self.active}, layer: {self.layer}, hitbox type: {self.hitbox_type}")

    def __repr__(self):
        return self.as_string

    def __str__(self):
        return self.as_string

    def on_mouse_left_press(self) -> None:
        if not self.enabled or not self.active:
            return

        if self.hover:
            self.pressed = True
            self.game.utilities.call_functions(self.invoke_on_press, (self,))

    def on_mouse_left_let(self) -> None:
        if not self.active:
            return

        if self.pressed:
            self.game.utilities.call_functions(self.invoke_on_let, (self,))

        self.pressed = False

    def clear_callbacks(self) -> None:
        self.invoke_on_press.clear()
        self.invoke_on_let.clear()

    def detach(self) -> None:
        self.clear_callbacks()
        self.ui_sheet.remove_element(self)
        self.game.inputs.on_mouse_left_press.remove(self._mouse_left_press_funka)
        self.game.inputs.on_mouse_left_let.remove(self._mouse_left_let_funka)

    def blit(self):
        blit_image: Surface = self.idle_image
        if not self.enabled:
            blit_image = self.disabled_image
        elif self.pressed:
            blit_image = self.pressed_image
        elif self.hover:
            blit_image = self.hover_image

        self.game.window.display.blit(blit_image, self.display_position)
