import pygame

from scripts.AssetClasses.Tilemap.Tiles.tile_component import TileComponent
from scripts.GameTypes import TilePosition, WorldPosition, DisplayPosition, GridPosition, OffgridTilePosition, \
    Percentage, Resolution, WorldRect, GridRect


class Tile:
    def __init__(self, grid: 'Grid', image: pygame.Surface, position: TilePosition,
                 offgrid: bool, alpha: Percentage, groups: set[str] | None=None):
        self.game = grid.game
        self.grid: 'Grid' = grid
        self._image: pygame.Surface = image
        self.position: TilePosition | OffgridTilePosition = position
        self.offgrid: bool = offgrid
        self.alpha: Percentage = alpha
        self.groups: set[str] = set() if groups is None else groups
        self.components: list[TileComponent] = []

        self._used_alpha: int = round(255 * self.alpha)
        self._alpha_image: pygame.Surface | None = None
        self._redo_image: bool = True

        self.blit_position_function: callable = self.get_blit_position
        self.blit_image_function: callable = self.get_blit_image
        self.alpha_image_function: callable = self.get_alpha_image
        self.offgrid_size_function: callable = self.get_offgrid_size

        # ongrid size is just tile_size
        # unite rects and images for ongrid?
        # easier collision detection for real tile size

        # we would need functions for all positions as they are required for correct rect, or expensive
        # we can change offgrid size now, not a problem for offgrid, while default position is used with combination

        # suggestion maybe well see
        # on_need_basis when well need grass well see, for now leave, maybe just add blit rects
        # in particular blit_rect() and world_blit_rect()

    @property
    def image(self) -> pygame.Surface:
        return self._image

    @property
    def used_alpha(self) -> int:
        return self._used_alpha

    @used_alpha.setter
    def used_alpha(self, alpha: Percentage):
        new_alpha: int = round(255 * alpha)

        if new_alpha != self._used_alpha:
            self._redo_image = True

        self._used_alpha = new_alpha

    @property
    def alpha_image(self) -> pygame.Surface:
        if self._used_alpha == 255:
            return self.image

        if not self._redo_image and self._alpha_image is not None:
            return self._alpha_image

        if self._alpha_image is None:
            self._alpha_image = self.image.copy()

        self._alpha_image.set_alpha(self.used_alpha)
        return self._alpha_image

    @property
    def size(self) -> Resolution:
        if self.offgrid:
            return self.offgrid_size_function(self)

        return self.grid.tile_size, self.grid.tile_size

    @property
    def clone(self) -> 'Tile':
        return self.game.utilities.load_tile(self.as_json, self.grid, self.offgrid)

    @property
    def as_json(self) -> dict:
        as_json: dict =  {
            "position": f"{self.position[0]};{self.position[1]}",
            "image": self.grid.get_name_of_image(self.image)
        }

        if self.alpha != 1:
            as_json["alpha"] = self.alpha

        if len(self.groups) > 0:
            as_json["groups"] = list(self.groups)

        if len(self.components) > 0:
            as_json["components"] = [component.as_json for component in self.components]

        return as_json

    @property
    def as_string(self) -> str:
        return (f"belongs to grid: {self.grid.name}, "
                f"image name: {self.grid.get_name_of_image(self.image)}, "
                f"position: {self.position}, "
                f"number of groups: {len(self.groups)}, "
                f"number of components: {len(self.components)}, "
                f"alpha: {self.alpha}")

    def __repr__(self):
        return self.as_string

    def __str__(self):
        return self.as_string

    @property
    def grid_position(self) -> GridPosition:
        if self.offgrid:
            return pygame.math.Vector2(*self.position)
        else:
            return self.grid.position_tile_to_grid(self.position)

    @property
    def world_position(self) -> WorldPosition:
        return self.grid.position_grid_to_world(self.grid_position)

    @property
    def display_position(self) -> DisplayPosition:
        return self.grid.position_grid_to_display(self.grid_position)

    def get_blit_position(self, _: 'Tile') -> DisplayPosition:
        return self.display_position

    def get_blit_image(self, _: 'Tile') -> pygame.Surface:
        return self.image

    def get_alpha_image(self, _: 'Tile') -> pygame.Surface:
        return self.alpha_image

    def get_offgrid_size(self, _: 'Tile') -> tuple[int, int]:
        return self.image.get_size()

    @property
    def grid_rect(self) -> GridRect:
        return pygame.FRect(*self.grid_position, *self.size)

    @property
    def rect(self) -> WorldRect:
        return pygame.FRect(*self.world_position, *self.size)

    @property
    def renderable(self) -> bool:
        return self.alpha != 0

    def blit(self) -> None:
        if not self.renderable:
            return

        self.game.window.display.blit(self.blit_image_function(self),
                                      self.blit_position_function(self))

    def blit_faded(self, alpha: Percentage) -> None:
        if not self.renderable:
            return

        self.used_alpha = alpha * self.alpha

        self.game.window.display.blit(self.alpha_image_function(self),
                                      self.blit_position_function(self))
