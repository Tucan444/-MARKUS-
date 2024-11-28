import pygame
from pygame import Surface, Vector2

from scripts.AssetClasses.UI.button import Button
from scripts.AssetClasses.UI.image import Image
from scripts.AssetClasses.UI.text import Text
from scripts.AssetClasses.UI.toggle import Toggle
from scripts.AssetClasses.UI.ui_element import UI_Element
from scripts.DataStructures.sorted_array import SortedArray
from scripts.GameTypes import UISheetPosition, HitboxType, Color, DisplayPosition, Resolution, Position, \
    SortableFunction, Percentage, SF_key


class Dropdown(UI_Element):
    def __init__(self, game: 'Game', ui_sheet: 'UI_Sheet', name: str,
                 position: UISheetPosition, layer: int, active: bool, input_wait: float,
                 selection_hitbox_type: HitboxType, option_hitbox_type: HitboxType,
                 selection_text: str, use_option_as_text: bool, text_padding: Percentage,
                 options: list[str], initial_option: int, enabled: bool,
                 selection: Surface, selection_hover: Surface,
                 selection_selected: Surface, selection_disabled: Surface,
                 option: Surface, option_hover: Surface,
                 selection_font: pygame.font.Font, selection_font_size: int, selection_bold: bool,
                 option_font: pygame.font.Font, option_font_size: int, option_bold: bool,
                 color_selection: Color, color_selection_hover: Color, color_selection_selected: Color,
                 color_option: Color, color_option_hover: Color,
                 options_background: Surface, options_foreground: Surface, scroll_speed: float):
        self.selection_hitbox_type: HitboxType = selection_hitbox_type
        self.option_hitbox_type: HitboxType = option_hitbox_type

        self._enabled: bool = False
        self.selection_text: str = selection_text
        self.use_option_as_text: bool = use_option_as_text
        self.text_padding_multiplier: Percentage = 1 - text_padding
        self.options: list[str] = options
        self.initial_option: int = initial_option
        self.selected_option_index: int = initial_option
        self.invoke_on_selection: SortedArray = SortedArray(SortableFunction, key=SF_key)
        self.invoke_on_dropdown_open: SortedArray = SortedArray(SortableFunction, key=SF_key)
        self.invoke_on_dropdown_close: SortedArray = SortedArray(SortableFunction, key=SF_key)

        self.scroll_position: float = 0
        self.scroll_speed: float = scroll_speed
        self._position: UISheetPosition = Vector2(0, 0)

        self.selection_size: Resolution = selection.get_size()
        self.option_size: Resolution = option.get_size()
        self.overlay_size: Resolution = options_background.get_size()
        self.overlay: Surface = pygame.Surface(self.overlay_size)

        assert(options_background.get_size() == options_foreground.get_size())
        assert(self.option_size[0] == self.overlay_size[0])

        self.selection: Toggle = Toggle(game, ui_sheet, f"{name}, selection", Vector2(0, 0),
                                        layer, True, input_wait, True, True, selection_hitbox_type,
                                        selection, selection_selected, selection_disabled, selection_disabled,
                                        selection_hover, selection_selected)

        self.selection_text_size: Resolution = (
            int(self.selection_size[0] * self.text_padding_multiplier),
            int(self.selection_size[1] * self.text_padding_multiplier)
        )
        self.selection_text_padding_shift: Position = Vector2(
            (self.selection_size[0] - self.selection_text_size[0]) * 0.5,
            (self.selection_size[1] - self.selection_text_size[1]) * 0.5
        )
        self.selection_text_ui: Text = Text(game, ui_sheet, self.selection_text_size, f"{name}, selection text",
                                            Vector2(0, 0), layer, True, selection_text, color_selection,
                                            color_selection_hover, color_selection_selected, True,
                                            selection_font, selection_font_size, selection_bold, True)

        self.background: Image = Image(game, ui_sheet, f"{name}, background", Vector2(0, 0),
                                       layer, False, HitboxType.RECTANGLE, options_background, options_background)
        self.foreground: Image = Image(game, ui_sheet, f"{name}, foreground", Vector2(0, 0),
                                       layer, False, HitboxType.RECTANGLE, options_foreground, options_foreground)

        self.option_image: Surface = option
        self.option_hover_image: Surface = option_hover
        self.options_ui: list[Button] = [
            Button(game, ui_sheet, f"{name}, option: {option_text}", Vector2(0, 0), layer, False,
                   input_wait, False, option_hitbox_type, option, option_hover, option_hover, option_hover)
            for option_text in self.options
        ]
        self.option_text_size: Resolution = (
            int(self.option_size[0] * self.text_padding_multiplier),
            int(self.option_size[1] * self.text_padding_multiplier)
        )
        self.option_text_padding_shift: Position = Vector2(
            (self.option_size[0] - self.option_text_size[0]) * 0.5,
            (self.option_size[1] - self.option_text_size[1]) * 0.5
        )

        self.color_option: Color = color_option
        self.color_option_hover: Color = color_option_hover
        self.option_font: pygame.font.Font = option_font
        self.option_font_size: int = option_font_size
        self.option_bold: bool = option_bold
        self.option_texts_ui: list[Text] = [
            Text(game, ui_sheet, self.option_text_size, f"{name}, option text: {option_text}", Vector2(0, 0),
                 layer, False, option_text, color_option, color_option_hover, color_option_hover,
                 False, option_font, option_font_size, option_bold, True)
            for option_text in self.options
        ]

        super().__init__(game, ui_sheet, selection.get_size(), name, position, layer, active,
                         input_wait, selection_hitbox_type)

        self.position = position
        self.enabled = enabled
        self.minimal_scroll: float = min(0., self.overlay.get_height() - ((len(self.options)+1) * self.option_size[1]))
        self.minimal_scroll *= 1 / self.option_size[1]
        if self.use_option_as_text:
            self.selection_text_ui.text = self.selected_option

        self._on_mouse_left_press_funka: SortableFunction = (
            self.input_wait, f"dropdown, {name}", self.on_mouse_left_press, self.ui_sheet
        )
        self._scroll_up_funka: SortableFunction = (
            self.input_wait, f"dropdown, {name}", self.mousewheel_scroll_up, self.ui_sheet
        )
        self._scroll_down_funka: SortableFunction = (
            self.input_wait, f"dropdown, {name}", self.mousewheel_scroll_down, self.ui_sheet
        )

        self.game.inputs.on_mouse_left_press.add(self._on_mouse_left_press_funka)
        self.game.inputs.on_mouse_scroll_up.add(self._scroll_up_funka)
        self.game.inputs.on_mouse_scroll_down.add(self._scroll_down_funka)

    @property
    def as_json(self) -> dict:
        json_form: dict = self.element_json

        image_names: dict[Surface, str] = self.game.assets.image_names

        json_form["type"] = "dropdown"
        json_form["selection hitbox type"] = self.selection_hitbox_type.value
        json_form["option hitbox type"] = self.option_hitbox_type.value
        json_form["selection text"] = self.selection_text
        json_form["use option as text"] = self.use_option_as_text
        json_form["text padding"] = 1 - self.text_padding_multiplier
        json_form["options"] = self.options
        json_form["initial option"] = self.initial_option
        json_form["enabled"] = self.enabled
        json_form["selection"] = image_names[self.selection.on_image]
        json_form["selection hover"] = image_names[self.selection.on_image_hover]
        json_form["selection selected"] = image_names[self.selection.off_image]
        json_form["selection disabled"] = image_names[self.selection.on_image_disabled]
        json_form["option"] = image_names[self.option_image]
        json_form["option hover"] = image_names[self.option_hover_image]
        json_form["selection font"] = self.game.assets.font_names[self.selection_text_ui.font]
        json_form["selection font size"] = self.selection_text_ui.font_size
        json_form["selection bold"] = self.selection_text_ui.bold
        json_form["option font"] = self.game.assets.font_names[self.option_font]
        json_form["option font size"] = self.option_font_size
        json_form["option bold"] = self.option_bold
        json_form["color selection"] = self.selection_text_ui.color_idle
        json_form["color selection hover"] = self.selection_text_ui.color_hover
        json_form["color selection pressed"] = self.selection_text_ui.color_pressed
        json_form["color option"] = self.color_option
        json_form["color option hover"] = self.color_option_hover
        json_form["options background"] = image_names[self.background.image]
        json_form["options foreground"] = image_names[self.foreground.image]
        json_form["scroll speed"] = self.scroll_speed

        return json_form

    @property
    def as_string(self) -> str:
        return (f"name: {self.name}, sheet name: {self.ui_sheet.name}, position: {self.position}, "
                f"enabled: {self.enabled}, selected option: {self.selected_option}, "
                f"number of options: {len(self.options)}, scroll speed: {self.scroll_speed}"
                f"active: {self.active}, layer: {self.layer}, hitbox type: {self.hitbox_type}")

    def __repr__(self):
        return self.as_string

    def __str__(self):
        return self.as_string

    @property
    def selected_option(self) -> str:
        return self.options[self.selected_option_index]

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, enabled: bool) -> None:
        self._enabled = enabled
        self.selection.enabled = enabled
        self.selection_text_ui.is_interactive = enabled

        if not enabled:
            self.selection_text_ui.color = self.selection_text_ui.color_pressed
            self.selection.is_on = True

    @property
    def position(self) -> UISheetPosition:
        return self._position

    @position.setter
    def position(self, position: UISheetPosition) -> None:
        self._position = position
        self._set_positions()

    def _set_positions(self) -> None:
        self.selection.position = self.position
        self.selection_text_ui.position = self.position + self.selection_text_padding_shift

    @property
    def intersecting_mouse(self) -> bool:
        if not self.active:
            return False

        intersecting_selection: bool = self.selection_intersecting_mouse

        if intersecting_selection or self.selection.is_on:
            return intersecting_selection

        return self.overlay_intersecting_mouse

    @property
    def selection_intersecting_mouse(self) -> bool:
        if not self.active:
            return False

        return self.game.utilities.collide_point(
            self.hitbox_type, self.rect, self.game.mouse.position
        )

    @property
    def overlay_intersecting_mouse(self) -> bool:
        if not self.active:
            return False

        return self.game.utilities.collide_point(
            HitboxType.RECTANGLE, self.overlay_rect, self.game.mouse.position
        )

    @property
    def selection_hover(self) -> bool:
        return self.selection_intersecting_mouse and (self == self.ui_sheet.top_element)

    @property
    def overlay_hover(self) -> bool:
        return self.overlay_intersecting_mouse and (self == self.ui_sheet.top_element)

    def option_hover(self, option_id: int, overlay_hover: bool|None = None) -> bool:

        if (not self.active or self.selection.is_on or
                self != self.ui_sheet.top_element or
                not (overlay_hover if overlay_hover is not None else self.overlay_hover)):
            return False

        return self.game.utilities.collide_point(
            self.option_hitbox_type, self.get_option_rect(option_id), self.game.mouse.position
        )

    @property
    def overlay_position(self) -> DisplayPosition:
        return self.display_position + Vector2(0, self.size[1])

    @property
    def overlay_local_position(self) -> Position:
        return self.position + Vector2(0, self.size[1])

    @property
    def overlay_rect(self) -> pygame.Rect:
        return pygame.Rect(*self.overlay_position, *self.overlay_size)

    def get_option_overlay_position(self, index: int) -> Position:
        return Vector2(0, (index * self.option_size[1]) + (self.scroll_position * self.option_size[1]))

    def get_option_position(self, index: int) -> DisplayPosition:
        return self.get_option_overlay_position(index) + self.overlay_position

    def get_option_rect(self, index: int) -> pygame.Rect:
        return pygame.Rect(*self.get_option_position(index), *self.option_size)

    def mousewheel_scroll_up(self) -> None:
        if not self.active or not self.enabled or not self.hover:
            return

        self.scroll_position += self.scroll_speed
        self.scroll_position = min(0., self.scroll_position)

    def mousewheel_scroll_down(self) -> None:
        if not self.active or not self.enabled or not self.hover:
            return

        self.scroll_position -= self.scroll_speed
        self.scroll_position = max(self.minimal_scroll, self.scroll_position)

    def on_mouse_left_press(self) -> None:
        dropdown_open: bool = not self.selection.is_on
        hover_selection: bool = self.selection_hover
        hover_overlay: bool = self.overlay_hover

        if not self.active or not self.enabled:
            return

        if dropdown_open and hover_overlay:
            for i in range(len(self.options)):
                if not self.option_hover(i):
                    continue

                self.selected_option_index = i
                self.game.utilities.call_functions(self.invoke_on_selection, (self,))
                if self.use_option_as_text:
                    self.selection_text_ui.text = self.selected_option

                break

        if not dropdown_open and hover_selection:
            self.selection.is_on = False
            self.selection_text_ui.is_interactive = False
            self.selection_text_ui.color = self.selection_text_ui.color_pressed
            self._overlay_set_active(True)
            self.game.utilities.call_functions(self.invoke_on_dropdown_open, (self,))
        elif dropdown_open and hover_selection:
            self.selection.is_on = True
            self.selection_text_ui.is_interactive = True
            self._overlay_set_active(False)
            self.game.utilities.call_functions(self.invoke_on_dropdown_close, (self,))
        elif dropdown_open and not hover_selection:
            self.selection.is_on = True
            self.selection_text_ui.is_interactive = True
            self._overlay_set_active(False)
            self.game.utilities.call_functions(self.invoke_on_dropdown_close, (self,))

    def _overlay_set_active(self, active: bool):
        self.background.active = active
        self.foreground.active = active

        for option, text in zip(self.options_ui, self.option_texts_ui):
            option.active = active
            text.active = active

    def clear_callbacks(self) -> None:
        self.invoke_on_selection.clear()
        self.invoke_on_dropdown_open.clear()
        self.invoke_on_dropdown_close.clear()

    def detach(self) -> None:
        self.clear_callbacks()
        self.ui_sheet.remove_element(self)
        self.game.inputs.on_mouse_left_press.remove(self._on_mouse_left_press_funka)
        self.game.inputs.on_mouse_scroll_up.remove(self._scroll_up_funka)
        self.game.inputs.on_mouse_scroll_down.remove(self._scroll_down_funka)

    def blit(self):
        if self.selection_hover and self.selection.is_on and self.enabled:
            self.game.window.display.blit(self.selection.on_image_hover, self.display_position)
            self.selection_text_ui.color = self.selection_text_ui.color_hover
            self.game.window.display.blit(self.selection_text_ui.image, self.selection_text_ui.text_display_position)
        else:
            self.selection.blit()
            self.selection_text_ui.blit()

        if not self.selection.is_on:
            self._blit_overlay()

    def _blit_overlay(self):
        overlay_hover: bool = self.overlay_hover

        self.overlay.fill((0, 0, 0))
        self.overlay.blit(self.background.image, (0, 0))

        for i in range(len(self.options)):
            option: Button = self.options_ui[i]
            text: Text = self.option_texts_ui[i]

            hover_option: bool = self.option_hover(i, overlay_hover)

            if hover_option:
                blit_image: Surface = option.hover_image
                text.color = text.color_hover
            else:
                blit_image: Surface = option.idle_image
                text.color = text.color_idle

            overlay_position: Position = self.get_option_overlay_position(i)
            self.overlay.blit(blit_image, overlay_position)

            overlay_position[0] += (text.size[0] - text.image.get_width()) * 0.5
            overlay_position[1] += (text.size[1] - text.image.get_height()) * 0.5
            overlay_position += self.option_text_padding_shift

            self.overlay.blit(text.image, overlay_position)

        self.overlay.blit(self.foreground.image, (0, 0))

        self.game.window.display.blit(self.overlay, self.overlay_position)
