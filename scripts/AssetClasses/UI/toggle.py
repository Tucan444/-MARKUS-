from pygame import Surface
from scripts.AssetClasses.UI.ui_element import UI_Element
from scripts.DataStructures.sorted_array import SortedArray
from scripts.GameTypes import UISheetPosition, Resolution, HitboxType, SortableFunction, SF_key


class Toggle(UI_Element):
    def __init__(self, game: 'Game', ui_sheet: 'UI_Sheet', name: str,
                 position: UISheetPosition, layer: int, active: bool, input_wait: float,
                 is_on: bool, enabled: bool, hitbox_type: HitboxType,
                 on_image: Surface, off_image: Surface,
                 on_image_disabled: Surface, off_image_disabled: Surface,
                 on_image_hover: Surface, off_image_hover: Surface):
        super().__init__(game, ui_sheet, on_image.get_size(), name, position, layer, active,
                         input_wait, hitbox_type)
        self.is_on: bool = is_on
        self.enabled: bool = enabled
        self.on_image: Surface = on_image
        self.on_image_disabled: Surface = on_image_disabled
        self.on_image_hover: Surface = on_image_hover
        self.off_image: Surface = off_image
        self.off_image_disabled: Surface = off_image_disabled
        self.off_image_hover: Surface = off_image_hover
        self.invoke_on_toggle: SortedArray = SortedArray(SortableFunction, key=SF_key)

        # size is size of self.on_image
        assert(self.on_image_disabled.get_size() == self.size)
        assert(self.on_image_hover.get_size() == self.size)
        assert(self.off_image.get_size() == self.size)
        assert(self.off_image_disabled.get_size() == self.size)
        assert(self.off_image_hover.get_size() == self.size)
        if self.hitbox_type == HitboxType.CIRCLE:
            assert(self.size[0] == self.size[1])

        self._mouse_left_press_funka: SortableFunction = (
            self.input_wait, f"toggle: {self.name}", self.on_mouse_left_press, self.ui_sheet
        )
        self.game.inputs.on_mouse_left_press.add(self._mouse_left_press_funka)

    @property
    def as_json(self) -> dict:
        json_form: dict = self.element_json

        image_names: dict[Surface, str] = self.game.assets.image_names

        json_form["type"] = "toggle"
        json_form["is_on"] = self.is_on
        json_form["enabled"] = self.enabled
        json_form["on image"] = image_names[self.on_image]
        json_form["on image disabled"] = image_names[self.on_image_disabled]
        json_form["on image hover"] = image_names[self.on_image_hover]
        json_form["off image"] = image_names[self.off_image]
        json_form["off image disabled"] = image_names[self.off_image_disabled]
        json_form["off image hover"] = image_names[self.off_image_hover]

        return json_form

    @property
    def as_string(self) -> str:
        return (f"name: {self.name}, sheet name: {self.ui_sheet.name}, is_on: {self.is_on}"
                f"position: {self.position}, enabled: {self.enabled}, "
                f"active: {self.active}, layer: {self.layer}, hitbox type: {self.hitbox_type}")

    def __repr__(self):
        return self.as_string

    def __str__(self):
        return self.as_string

    def on_mouse_left_press(self) -> None:
        if not self.enabled:
            return

        if self.hover:
            self.is_on = not self.is_on

            self.game.utilities.call_functions(self.invoke_on_toggle, (self,))

    def clear_callbacks(self) -> None:
        self.invoke_on_toggle.clear()

    def detach(self) -> None:
        self.clear_callbacks()
        self.ui_sheet.remove_element(self)
        self.game.inputs.on_mouse_left_press.remove(self._mouse_left_press_funka)

    def blit(self):
        hover: bool = self.hover
        blit_image: Surface = self.on_image

        if self.is_on:
            if not self.enabled:
                blit_image = self.on_image_disabled
            elif hover:
                blit_image = self.on_image_hover
        else:
            blit_image = self.off_image
            if not self.enabled:
                blit_image = self.off_image_disabled
            elif hover:
                blit_image = self.off_image_hover

        self.game.window.display.blit(blit_image, self.display_position)
