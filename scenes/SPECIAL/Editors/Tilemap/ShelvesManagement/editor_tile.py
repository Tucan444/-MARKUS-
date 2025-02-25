import pygame.transform
from pygame import Surface

from scripts.AssetClasses.Tilemap.Tiles.tile import Tile
from scripts.AssetClasses.Tilemap.grid import Grid
from scripts.GameTypes import Color, Resolution, Position


class EditorTile:
    def __init__(self, shelf: 'Shelf', tile_data: dict, preview_data: dict):
        self.game: 'Game' = shelf.game
        self.shelf: 'Shelf' = shelf
        self.tile_data: dict = tile_data

        self.preview_color: Color = preview_data["color"] if "color" in preview_data else None
        self.preview_image_name: str = preview_data["image"] if "image" in preview_data else None
        self.preview_animation_name: str = tile_data["animation"] if "animation" in tile_data else None

        self._check_preview_validity()

        self.ui_image: Surface = self._get_ui_image()
        self.ui_size: Resolution = self.ui_image.get_size()

    def _check_preview_validity(self) -> None:
        none_count: int = (1 if self.preview_color else 0) + (1 if self.preview_image_name else 0)
        assert none_count < 2

        if none_count == 1:
            return

        if self.preview_animation_name is None and "image" in self.tile_data:
            self.preview_image_name = self.tile_data["image"]
            return

        assert self.preview_animation_name is not None

    @property
    def _preview_type(self) -> int:
        preview_type: int = 2
        if self.preview_image_name is not None:
            preview_type = 1
        elif self.preview_color is not None:
            preview_type = 0

        return preview_type

    def _get_ui_image(self) -> Surface:
        preview_type: int = self._preview_type

        if preview_type == 0:
            img: Surface = Surface((self.shelf.item_width, self.shelf.item_width))
            img.fill(self.preview_color)
            return img

        elif preview_type == 1:
            img: Surface = self.game.assets.images[self.preview_image_name]

        elif preview_type == 2:
            img: Surface = self.game.assets.animations[self.preview_animation_name].image

        else:
            raise Exception(f"preview type is not in [0, 1, 2], actual: {preview_type}")

        #new_height: int = int((self.shelf.item_width / img.get_width()) * img.get_height())
        #img = pygame.transform.scale(img, (self.shelf.item_width, new_height))
        img = pygame.transform.scale(img, (self.shelf.item_width, self.shelf.item_width))
        return img

    def get_preview_image(self, grid: Grid, offgrid: bool) -> Surface:
        preview_type: int = self._preview_type
        size: Resolution = (grid.tile_size, grid.tile_size)
        image: Surface = None

        if offgrid:
            if self.preview_image_name is not None:
                image = self.game.assets.images[self.preview_image_name]
            elif self.preview_animation_name is not None:
                image = self.game.assets.animations[self.preview_animation_name].image

            size = image.get_size()

        if preview_type == 0:
            img: Surface = Surface(size)
            img.fill(self.preview_color)
            return img
        elif preview_type == 1 and offgrid:
            return self.game.assets.images[self.preview_image_name]
        elif preview_type == 2 and offgrid:
            return self.game.assets.animations[self.preview_animation_name].image

        elif preview_type == 1 and not offgrid:
            img = self.game.assets.images[self.preview_image_name]
            return pygame.transform.scale(img, size)
        elif preview_type == 2 and not offgrid:
            img = self.game.assets.animations[self.preview_animation_name].image
            return pygame.transform.scale(img, size)

        return image

    def get_tile_object(self, grid: Grid, offgrid: bool, position: Position) -> Tile:
        self.tile_data["position"] = (f"{position[0] if offgrid else int(position[0])};"
                                      f"{position[1] if offgrid else int(position[1])}")

        return self.game.utilities.load_tile(self.tile_data, grid, offgrid)
