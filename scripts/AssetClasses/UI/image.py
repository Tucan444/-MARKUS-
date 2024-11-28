from pygame import Surface

from scripts.AssetClasses.UI.ui_element import UI_Element
from scripts.GameTypes import UISheetPosition, HitboxType


class Image(UI_Element):
    def __init__(self, game: 'Game', ui_sheet: 'UI_Sheet', name: str,
                 position: UISheetPosition, layer: int, active: bool,
                 hitbox_type: HitboxType, image: Surface, image_hover: Surface):
        super().__init__(game, ui_sheet, image.get_size(), name, position, layer, active,
                         hitbox_type=hitbox_type)

        self.image: Surface = image
        self.image_hover: Surface = image_hover

    @property
    def as_json(self) -> dict:
        json_form: dict = self.element_json

        image_names: dict[Surface, str] = self.game.assets.image_names

        json_form["type"] = "image"
        json_form["image"] = image_names[self.image]
        json_form["image hover"] = image_names[self.image_hover]

        return json_form

    def blit(self):
        self.game.window.display.blit(self.image if not self.hover else self.image_hover,
                                      self.display_position)
