import pygame
from scripts.GameTypes import UISheetPosition, Resolution, DisplayPosition, HitboxType


class UI_Element:
    def __init__(self, game: 'Game', ui_sheet: 'UI_Sheet', size: Resolution, name: str,
                 position: UISheetPosition, layer: int, active: bool, input_wait: float=0,
                 hitbox_type: HitboxType=HitboxType.RECTANGLE):
        self.game: 'Game' = game
        self.ui_sheet: 'UI_Sheet' = ui_sheet
        self.size: Resolution = size
        self.name: str = name
        self.position: UISheetPosition = position
        self.layer: int = layer
        self.input_wait: float = input_wait
        self._active: bool = active
        self.hitbox_type: HitboxType = hitbox_type

    @property
    def element_json(self) -> dict:
        return {
            "type": "ui element",
            "size": [*self.size],
            "name": self.name,
            "position": list(self.position),
            "layer": self.layer,
            "input wait": self.input_wait,
            "active": self.active,
            "hitbox type": self.hitbox_type.value
        }

    @property
    def as_json(self) -> dict:
        return self.element_json

    @property
    def as_string(self) -> str:
        return (f"name: {self.name}, sheet name: {self.ui_sheet.group}, position: {self.position}, "
                f"active: {self.active}, layer: {self.layer}, hitbox type: {self.hitbox_type}")

    def __repr__(self):
        return self.as_string

    def __str__(self):
        return self.as_string

    @property
    def clone(self) -> 'UI_Element':
        return self.game.utilities.load_ui_element(self.as_json, self.game, self.ui_sheet)

    @property
    def active(self) -> bool:
        return self._active and self.ui_sheet.active

    @active.setter
    def active(self, active: bool) -> None:
        self._active = active

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(*self.display_position, *self.size)

    @property
    def intersecting_mouse(self) -> bool:
        if not self.active:
            return False

        return self.game.utilities.collide_point(
            self.hitbox_type, self.rect, self.game.mouse.position
        )

    @property
    def hover(self) -> bool:
        return self.intersecting_mouse and (self == self.ui_sheet.top_element)

    @property
    def display_position(self) -> DisplayPosition:
        return self.ui_sheet.position_sheet_to_display(self.position)

    def clear_callbacks(self) -> None:
        pass

    def detach(self) -> None:
        self.ui_sheet.remove_element(self)

    def blit(self):
        pass
