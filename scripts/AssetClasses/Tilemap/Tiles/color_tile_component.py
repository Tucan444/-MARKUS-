import pygame

from scripts.AssetClasses.Tilemap.Tiles.tile import Tile
from scripts.AssetClasses.Tilemap.Tiles.tile_component import TileComponent
from scripts.GameTypes import Color


class ColorTileComponent(TileComponent):
    def __init__(self, tile: Tile, color: Color) -> None:
        super().__init__(tile)
        self._colored_image: pygame.Surface = pygame.Surface(self.tile.size)
        self._color: Color = None

        self.color = color
        self.tile.blit_image_function = self.get_blit_image
        self.tile.alpha_image_function = self.get_blit_image

    @property
    def color(self) -> Color:
        return self._color

    @color.setter
    def color(self, new_color: Color) -> None:
        self._color = new_color
        self._colored_image.fill(self._color)

    @property
    def as_json(self) -> dict:
        return {
            "class_name": self.__class__.__name__,
            "color": list(self.color)
        }

    @classmethod
    def load(cls, component_data: dict, tile: 'Tile') -> 'Component':
        return cls(tile, tuple(component_data["color"]))

    def get_blit_image(self, _: Tile) -> pygame.Surface:
        return self._colored_image
