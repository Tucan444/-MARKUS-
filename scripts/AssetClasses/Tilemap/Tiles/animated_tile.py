from scripts.AssetClasses.Tilemap.grid import Grid
from scripts.AssetClasses.Tilemap.Tiles.tile import Tile
import pygame

from scripts.AssetClasses.Animation.animation import Animation
from scripts.GameTypes import Percentage, TilePosition


class AnimatedTile(Tile):
    def __init__(self, grid: 'Grid', animation: Animation, position: TilePosition,
                 offgrid: bool, clone_animation: bool, alpha: Percentage, groups: set[str] | None=None):
        super().__init__(grid, None, position, offgrid, alpha, groups)

        self.animation: Animation = animation
        self.uncloned_animation: Animation = animation
        self.animation_cloned: bool = clone_animation

        if clone_animation:
            self.animation = self.animation.clone

        self._last_alpha_animation_frame: int = -1

    @property
    def alpha_image(self) -> pygame.Surface:
        if self._used_alpha == 255:
            return self.animation.image

        frame_changed: bool = self._last_alpha_animation_frame != self.animation.current_frame

        if frame_changed:
            self._last_alpha_animation_frame = self.animation.current_frame
            self._redo_image = True

        if not self._redo_image and self._alpha_image is not None:
            return self._alpha_image

        if self._alpha_image is None or frame_changed:
            self._alpha_image = self.animation.image.copy()

        self._alpha_image.set_alpha(self.used_alpha)
        return self._alpha_image

    @property
    def image(self) -> pygame.Surface:
        return self.animation.image

    @property
    def clone(self) -> 'AnimatedTile':
        return self.game.utilities.load_tile(self.as_json, self.grid, self.offgrid)

    @property
    def as_json(self) -> dict:
        as_json: dict = {
            "position": f"{self.position[0]};{self.position[1]}",
            "animation": self.grid.get_name_of_animation(self.uncloned_animation)
        }

        if self.alpha != 1:
            as_json["alpha"] = self.alpha

        if self.animation_cloned:
            as_json["clone_animation"] = True

        if len(self.groups) > 0:
            as_json["groups"] = list(self.groups)

        if len(self.components) > 0:
            as_json["components"] = [component.as_json for component in self.components.values()]

        return as_json

    @property
    def as_string(self) -> str:
        return (f"belongs to grid: {self.grid.group}, "
                f"animation name: {self.grid.get_name_of_animation(self.uncloned_animation)}, "
                f"position: {self.position}, "
                f"number of groups: {len(self.groups)}, "
                f"number of components: {len(self.components)}, "
                f"alpha: {self.alpha}")

    def __repr__(self):
        return self.as_string

    def __str__(self):
        return self.as_string
