import copy

from pygame import Surface, Vector2

from scripts.AssetClasses.UI.Groups.ui_group import UI_Group
from scripts.AssetClasses.UI.ui_element import UI_Element
from scripts.GameTypes import UISheetPosition, HitboxType, SortableFunction, UISheetVector, Range


class ScrollZone(UI_Element):
    def __init__(self, game: 'Game', ui_sheet: 'UI_Sheet', name: str, position: UISheetPosition,
                 layer: int, active: bool, hitbox_type: HitboxType, input_wait: float,
                 enabled: bool, image: Surface, image_hover: Surface, image_disabled: Surface,
                 scroll_speed: float, scroll_bounds: tuple[Range, Range],
                 vertical: bool, flip_direction: bool):

        self.enabled: bool = enabled
        self.image: Surface = image
        self.image_hover: Surface = image_hover
        self.image_disabled: Surface = image_disabled

        self.group: UI_Group = UI_Group(ui_sheet, f"scroll zone: {name}")
        self.scroll_speed: float = scroll_speed
        self.scroll_position: UISheetPosition = Vector2(0, 0)
        self.x_scroll_bound: Range = scroll_bounds[0]
        self.y_scroll_bound: Range = scroll_bounds[1]
        self.vertical: bool = vertical
        self.flip_direction: bool = flip_direction

        super().__init__(game, ui_sheet, image.get_size(), name, position, layer, active,
                         input_wait, hitbox_type)

        self.scroll_up_funka: SortableFunction = (
            self.input_wait, f"scroll zone, {name}", self.mousewheel_scroll_up, self.ui_sheet)
        self.scroll_down_funka: SortableFunction = (
            self.input_wait, f"scroll zone, {name}", self.mousewheel_scroll_down, self.ui_sheet)

        self.game.inputs.on_mouse_scroll_up.add(self.scroll_up_funka)
        self.game.inputs.on_mouse_scroll_down.add(self.scroll_down_funka)

    @property
    def as_json(self) -> dict:
        json_form: dict = self.element_json

        image_names: dict[Surface, str] = self.game.assets.image_names

        json_form["type"] = "scroll zone"
        json_form["enabled"] = self.enabled
        json_form["image"] = image_names[self.image]
        json_form["image hover"] = image_names[self.image_hover]
        json_form["image disabled"] = image_names[self.image_disabled]
        json_form["scroll speed"] = self.scroll_speed
        json_form["scroll bounds"] = [ list(self.x_scroll_bound), list(self.y_scroll_bound) ]
        json_form["vertical"] = self.vertical
        json_form["flip direction"] = self.flip_direction
        json_form["zone elements"] = [
            element.group for element in self.group.elements
        ]

        return json_form

    @property
    def as_string(self) -> str:
        return (f"name: {self.name}, sheet name: {self.ui_sheet.name}, position: {self.position}, "
                f"enabled: {self.enabled}, number of elements: {len(self.group.elements)}, "
                f"vertical: {self.vertical}, flip direction: {self.flip_direction}, "
                f"scroll position: {self.scroll_position}, scroll speed: {self.scroll_speed}"
                f"active: {self.active}, layer: {self.layer}, hitbox type: {self.hitbox_type}")

    def __repr__(self):
        return self.as_string

    def __str__(self):
        return self.as_string

    @property
    def scroll_vector(self) -> UISheetVector:
        return (-1 if self.flip_direction else 1) * Vector2(
            self.scroll_speed if not self.vertical else 0,
            -self.scroll_speed if self.vertical else 0
        )

    def _bound_scroll_position(self) -> None:
        original_scroll: UISheetPosition = copy.copy(self.scroll_position)

        self.scroll_position[0] = max(self.x_scroll_bound[0], min(self.x_scroll_bound[1], self.scroll_position[0]))
        self.scroll_position[1] = max(self.y_scroll_bound[0], min(self.y_scroll_bound[1], self.scroll_position[1]))

        difference: UISheetVector = self.scroll_position - original_scroll
        self.group.move_elements(difference)

    def mousewheel_scroll_up(self) -> None:
        if not self.active or not self.enabled or not self.intersecting_mouse:
            return

        self.scroll_position += self.scroll_vector
        self.group.move_elements(self.scroll_vector)
        self._bound_scroll_position()

    def mousewheel_scroll_down(self) -> None:
        if not self.active or not self.enabled or not self.intersecting_mouse:
            return

        self.scroll_position -= self.scroll_vector
        self.group.move_elements(-self.scroll_vector)
        self._bound_scroll_position()

    def undo_scroll(self) -> None:
        self.group.move_elements(-self.scroll_position)
        self.scroll_position = Vector2(0, 0)

    def add_element(self, element: UI_Element) -> None:
        self.group.elements.add(element)

    def add_elements(self, *args) -> None:
        for element in args:
            assert(issubclass(type(element), UI_Element))
            self.group.elements.add(element)

    def move_with_elements(self, vector: UISheetVector) -> None:
        self.position += vector
        self.group.move_elements(vector)

    def detach(self) -> None:
        self.ui_sheet.remove_element(self)
        self.game.inputs.on_mouse_scroll_up.remove(self.scroll_up_funka)
        self.game.inputs.on_mouse_scroll_down.remove(self.scroll_down_funka)

    def blit(self):
        blit_image: Surface = self.image

        if not self.enabled:
            blit_image = self.image_disabled
        elif self.intersecting_mouse:
            blit_image = self.image_hover

        self.game.window.display.blit(blit_image, self.display_position)
