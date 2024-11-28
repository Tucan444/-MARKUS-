import pygame
from scripts.AssetClasses.UI.ui_element import UI_Element
from scripts.DataStructures.sorted_array import SortedArray
from scripts.GameTypes import UISheetPosition, Color, Resolution, DisplayPosition, SortableFunction, SF_key


class Text(UI_Element):
    def __init__(self, game: 'Game', ui_sheet: 'UI_Sheet', size: Resolution,
                 name: str, position: UISheetPosition, layer: int, active: bool,
                 text: str,  color_idle: Color, color_hover: Color, color_pressed: Color,
                 is_interactive: bool, font: pygame.font.Font,
                 font_size: int, bold: bool, centered: bool, visualize_boundary: bool=False):
        super().__init__(game, ui_sheet, size, name, position, layer, active)
        self._text: str = text
        self._color: Color = color_idle
        self.color_idle: Color = color_idle
        self.color_hover: Color = color_hover
        self.color_pressed: Color = color_pressed
        self.is_interactive: bool = is_interactive
        self.font: pygame.font.Font = font

        self.visualize_boundary: bool = visualize_boundary

        self._font_size: int = font_size
        self._bold: bool = bold
        self.centered: bool = centered

        self._size_shadow: Resolution = size
        self._image_is_up_to_date: bool = False
        self._image: pygame.Surface | None = None

        self.pressed: bool = False
        
        self.invoke_on_press: SortedArray = SortedArray(SortableFunction, key=SF_key)
        self.invoke_on_let: SortedArray = SortedArray(SortableFunction, key=SF_key)
        
        self._mouse_left_press_funka: SortableFunction = (
            self.input_wait, f"text: {self.name}", self.on_mouse_left_press, self.ui_sheet)
        self._mouse_left_let_funka: SortableFunction = (
            self.input_wait, f"text: {self.name}", self.on_mouse_left_let, self.ui_sheet)

        self.game.inputs.on_mouse_left_press.add(self._mouse_left_press_funka)
        self.game.inputs.on_mouse_left_let.add(self._mouse_left_let_funka)

    @property
    def as_json(self) -> dict:
        json_form: dict = self.element_json

        json_form["type"] = "text"
        json_form["text"] = self.text
        json_form["color idle"] = self.color_idle
        json_form["color hover"] = self.color_hover
        json_form["color pressed"] = self.color_pressed
        json_form["is interactive"] = self.is_interactive
        json_form["font"] = self.game.assets.font_names[self.font]
        json_form["font size"] = self.font_size
        json_form["bold"] = self.bold
        json_form["centered"] = self.centered
        json_form["visualize boundary"] = self.visualize_boundary

        return json_form

    @property
    def as_string(self) -> str:
        return (f"name: {self.name}, sheet name: {self.ui_sheet.name}, position: {self.position}, "
                f"text: {self.text}, color: {self.color}, font size: {self.font_size}, bold: {self.bold}, "
                f"centered: {self.centered}"
                f"active: {self.active}, layer: {self.layer}, hitbox type: {self.hitbox_type}")

    def __repr__(self):
        return self.as_string

    def __str__(self):
        return self.as_string

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, text: str) -> None:
        if text == self._text:
            return

        self._text = text
        self._image_is_up_to_date = False

    @property
    def color(self) -> Color:
        return self._color

    @color.setter
    def color(self, color: Color) -> None:
        if color == self._color:
            return

        self._color = color
        self._image_is_up_to_date = False

    @property
    def font_size(self) -> int:
        return self._font_size

    @font_size.setter
    def font_size(self, font_size: int) -> None:
        if font_size == self._font_size:
            return

        self._font_size = font_size
        self._image_is_up_to_date = False

    @property
    def bold(self) -> bool:
        return self._bold

    @bold.setter
    def bold(self, bold: bool) -> None:
        if bold == self._bold:
            return

        self._bold = bold
        self._image_is_up_to_date = False

    @property
    def text_display_position(self) -> DisplayPosition:
        if not self.centered:
            return self.display_position

        return self.centered_display_position

    @property
    def text_rect(self) -> pygame.Rect:
        return pygame.Rect(*self.text_display_position, *self.image.get_size())

    @property
    def intersecting_mouse(self) -> bool:
        if not self.active:
            return False

        return self.game.utilities.collide_point(
            self.hitbox_type, self.text_rect, self.game.mouse.position
        )

    @property
    def image(self) -> pygame.Surface:
        if self.size != self._size_shadow:
            self._image_is_up_to_date = False
            self._size_shadow = self.size

        if self._image_is_up_to_date and self._image is not None:
            return self._image

        self.font.set_point_size(self.font_size)
        self.font.set_bold(self.bold)
        self._image = self.font.render(self.text, False, self.color)

        oversize: float = min(self.size[0] / self._image.get_width(), self.size[1] / self._image.get_height())
        if oversize < 1:
            new_text_size: Resolution = self._image.get_size()
            new_text_size = (int(new_text_size[0] * oversize), int(new_text_size[1] * oversize))
            self._image = pygame.transform.scale(self._image, new_text_size)

        self._image_is_up_to_date = True

        return self._image

    @property
    def centered_display_position(self) -> DisplayPosition:
        position: DisplayPosition = self.display_position

        position[0] += (self.size[0] - self.image.get_width()) * 0.5
        position[1] += (self.size[1] - self.image.get_height()) * 0.5

        return position
    
    def on_mouse_left_press(self) -> None:
        if not self.is_interactive or not self.active:
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
        if self.visualize_boundary:
            rect_surf: pygame.Surface = pygame.Surface(self.size)
            rect_surf.set_alpha(100)
            rect_surf.fill((150, 150, 255))

            self.game.window.display.blit(rect_surf, self.display_position)

        if self.is_interactive:
            if self.pressed:
                self.color = self.color_pressed
            elif self.hover:
                self.color = self.color_hover
            else:
                self.color = self.color_idle

        self.game.window.display.blit(self.image, self.text_display_position)
