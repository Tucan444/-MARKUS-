import pygame
from pygame.math import Vector2

from scripts.AssetClasses.Tilemap.gridcaster import Gridcaster
from scripts.AssetClasses.Tilemap.Tiles.tile import Tile
from scripts.AssetClasses.animation import Animation
from scripts.GameTypes import TilePosition, Resolution, GridPosition, WorldPosition, Percentage, \
    DisplayPosition, FocusedVector, TileHitInfo, WorldRay, GridRay, IntRange


class Grid:
    def __init__(self, tilemap: 'Tilemap', name: str, tile_size: int, layer: int,
                 active: bool, depth: float, use_depth: bool, invisible: bool,
                 physical: bool, alpha: Percentage, ongrid_padding: int):
        self.game: 'Game' = tilemap.game
        self.tilemap: 'Tilemap' = tilemap
        self.name: str = name
        self.tile_size: int = tile_size
        self._alpha = alpha
        self.layer: int = layer
        self.active: bool = active

        self._depth: float = depth
        self.depth_from_grid: float = 2 ** -depth  # depth to grid is just inverse (1/depth from grid)
        self.use_depth: bool = use_depth

        self.invisible: bool = invisible
        self.physical: bool = physical
        self.ongrid_padding: int = ongrid_padding

        self.tiles: dict[TilePosition, Tile] = {}

        self.offgrid_background: set[Tile] = set()
        self.offgrid_foreground: set[Tile] = set()

    @property
    def tile_count(self) -> int:
        return len(self.tiles) + len(self.offgrid_foreground) + len(self.offgrid_background)

    @property
    def clone(self) -> 'Grid':
        return self.game.utilities.load_grid(self.as_json, self.tilemap)

    @property
    def as_json(self) -> dict:
        return {
            "name": self.name,
            "tile size": self.tile_size,
            "alpha": self.alpha,
            "layer": self.layer,
            "active": self.active,
            "depth": self.depth,
            "use depth": self.use_depth,
            "invisible": self.invisible,
            "physical": self.physical,
            "ongrid padding": self.ongrid_padding,
            "tiles": [tile.as_json for tile in self.tiles.values()],
            "offgrid background": [tile.as_json for tile in self.offgrid_background],
            "offgrid foreground": [tile.as_json for tile in self.offgrid_foreground]
        }

    @property
    def as_string(self) -> str:
        return (f"belongs to tilemap: {self.tilemap.group}, "
                f"name: {self.name}, "
                f"tile size: {self.tile_size}, "
                f"tile count: {self.tile_count}, "
                f"active: {self.active}, "
                f"layer: {self.layer}, "
                f"invisible: {self.invisible}, "
                f"use depth: {self.use_depth}, "
                f"depth: {self.depth}, "
                f"physical: {self.physical}, "
                f"ongrid padding: {self.ongrid_padding}")

    def __repr__(self):
        return self.as_string

    def __str__(self):
        return self.as_string

    @property
    def depth(self) -> float:
        return self._depth

    @depth.setter
    def depth(self, depth: float) -> None:
        self._depth = depth
        self.depth_from_grid = 2 ** -self._depth

    @property
    def alpha(self) -> Percentage:
        return self._alpha * self.tilemap.alpha

    @alpha.setter
    def alpha(self, alpha: Percentage) -> None:
        self._alpha = alpha

    def position_grid_to_display(self, position: GridPosition) -> DisplayPosition:
        if self.use_depth:
            display_vec: FocusedVector = self.tilemap.focused_position * self.depth_from_grid

            return position + display_vec + self.game.window.display_center
        else:
            return position + self.tilemap.display_position

    def position_display_to_grid(self, position: DisplayPosition) -> GridPosition:
        if self.use_depth:
            display_vec: FocusedVector = self.tilemap.focused_position * self.depth_from_grid

            return position - display_vec - self.game.window.display_center
        else:
            return position - self.tilemap.display_position

    def position_world_to_grid(self, position: WorldPosition) -> GridPosition:
        if self.use_depth:
            return self.position_display_to_grid(self.game.camera.position_world_to_display(position))
        else:
            return position - self.tilemap.position

    def position_grid_to_world(self, position: GridPosition) -> WorldPosition:
        if self.use_depth:
            return self.game.camera.position_display_to_world(self.position_grid_to_display(position))
        else:
            return position + self.tilemap.position

    def position_grid_to_tile(self, position: GridPosition) -> TilePosition:
        return (
            int(position[0] // self.tile_size),
            int(position[1] // self.tile_size)
        )

    def position_tile_to_grid(self, position: TilePosition) -> GridPosition:
        return Vector2(
            position[0] * self.tile_size,
            position[1] * self.tile_size
        )

    def position_world_to_tile(self, position: WorldPosition) -> TilePosition:
        return self.position_grid_to_tile(self.position_world_to_grid(position))

    def position_tile_to_world(self, position: TilePosition) -> WorldPosition:
        return self.position_grid_to_world(self.position_tile_to_grid(position))

    def position_tile_to_display(self, position: TilePosition) -> DisplayPosition:
        return self.position_grid_to_display(self.position_tile_to_grid(position))

    def position_display_to_tile(self, position: DisplayPosition) -> TilePosition:
        return self.position_grid_to_tile(self.position_display_to_grid(position))

    # image operations next 3, then animation operations next 3
    def rescale_image_for_grid(self, image_name: str) -> bool:
        if image_name not in self.tilemap.game.assets.images:
            return False

        if self.tile_size not in self.tilemap.tilemap_resized_images:
            self.tilemap.tilemap_resized_images[self.tile_size] = {}
            self.tilemap.resized_image_names[self.tile_size] = {}

        if image_name in self.tilemap.tilemap_resized_images[self.tile_size]:
            return True

        original: pygame.Surface = self.tilemap.game.assets.images[image_name]
        new_resolution: Resolution = (self.tile_size, self.tile_size)

        if original.get_size() == new_resolution:
            return True

        resized_image: pygame.Surface = pygame.transform.scale(original, new_resolution)

        self.tilemap.tilemap_resized_images[self.tile_size][image_name] = resized_image
        self.tilemap.resized_image_names[self.tile_size][resized_image] = image_name

        return True

    def get_image(self, image_name: str) -> pygame.Surface:
        if self.tile_size in self.tilemap.tilemap_resized_images:
            if image_name in self.tilemap.tilemap_resized_images[self.tile_size]:
                return self.tilemap.tilemap_resized_images[self.tile_size][image_name]

        return self.game.assets.images[image_name]

    def get_name_of_image(self, image: pygame.Surface) -> str:
        if image in self.game.assets.image_names:
            return self.game.assets.image_names[image]

        if self.tile_size not in self.tilemap.resized_image_names:
            return "IMAGE MISSING, NO SUCH RESOLUTION IN RESIZED IMAGES"

        if image not in self.tilemap.resized_image_names[self.tile_size]:
            return "IMAGE MISSING, IMAGE NOT IN RESIZED IMAGES"

        return self.tilemap.resized_image_names[self.tile_size][image]

    def rescale_animation_for_grid(self, animation_name: str) -> bool:
        if animation_name not in self.tilemap.game.assets.animations:
            return False

        if self.tile_size not in self.tilemap.tilemap_resized_animations:
            self.tilemap.tilemap_resized_animations[self.tile_size] = {}
            self.tilemap.resized_animation_names[self.tile_size] = {}

        if animation_name in self.tilemap.tilemap_resized_animations[self.tile_size]:
            return True

        original: Animation = self.tilemap.game.assets.animations[animation_name]
        original_frames: list[pygame.Surface] = original.frames
        new_resolution: Resolution = (self.tile_size, self.tile_size)

        original.frames = [
            pygame.transform.scale(frame, new_resolution) for frame in original.frames_clone]
        resized_animation: Animation = original.hard_clone
        original.frames = original_frames

        self.tilemap.tilemap_resized_animations[self.tile_size][animation_name] = resized_animation
        self.tilemap.resized_animation_names[self.tile_size][resized_animation] = animation_name

        return True

    def get_animation(self, animation_name: str) -> Animation:
        assert self.tile_size in self.tilemap.tilemap_resized_animations
        assert animation_name in self.tilemap.tilemap_resized_animations[self.tile_size]

        return self.tilemap.tilemap_resized_animations[self.tile_size][animation_name]

    def get_name_of_animation(self, animation: Animation) -> str:
        assert self.tile_size in self.tilemap.resized_animation_names
        assert animation in self.tilemap.resized_animation_names[self.tile_size]

        return self.tilemap.resized_animation_names[self.tile_size][animation]

    def raycast(self, ray: WorldRay, known_hit: TileHitInfo=(-1, None)) -> TileHitInfo:
        best_hit: TileHitInfo = self.raycast_offgrid(ray, known_hit)
        best_hit = self.raycast_ongrid(ray, best_hit)
        return best_hit

    def raycast_offgrid(self, ray: WorldRay, known_hit: TileHitInfo=(-1, None)) -> TileHitInfo:
        grid_ray: GridRay = ray.clone
        grid_ray.position = self.position_world_to_grid(grid_ray.position)

        best_hit: TileHitInfo = known_hit

        for tile in self.offgrid_background:
            time = grid_ray.cast_against_rect(tile.grid_rect)

            hit: bool = time >= 0
            better_option: bool = time < best_hit[0] or best_hit[0] < 0
            if hit and better_option:
                best_hit = (time, tile)

        for tile in self.offgrid_foreground:
            time = grid_ray.cast_against_rect(tile.grid_rect)

            hit: bool = time >= 0
            better_option: bool = time < best_hit[0] or best_hit[0] < 0
            if hit and better_option:
                best_hit = (time, tile)

        return best_hit

    def raycast_ongrid(self, ray: WorldRay, known_hit: TileHitInfo=(-1, None), visualize: bool=False) -> TileHitInfo:
        gridcaster: Gridcaster = self.get_gridcaster(ray, known_hit)
        gridcaster.init(visualize)
        gridcaster.cast(visualize)

        return gridcaster.best_hit

    def get_gridcaster(self, ray: WorldRay, known_hit=(-1, None)) -> Gridcaster:
        grid_ray: GridRay = ray.clone
        grid_ray.position = self.position_world_to_grid(grid_ray.position)

        return Gridcaster(self.game, self, grid_ray, known_hit)

    def get_onscreen_tiles(self) -> list[Tile]:
        if not self.active:
            return []

        camera_pos: GridPosition = self.position_world_to_grid(self.tilemap.game.camera.position)
        camera_tile_pos: TilePosition = self.position_grid_to_tile(camera_pos)
        camera_bound_tile_pos: TilePosition = self.position_grid_to_tile(camera_pos + Vector2(*self.game.window.display_size))
        camera_rect: pygame.FRect = pygame.FRect(*camera_pos, *self.game.window.display_size)

        tiles: list[Tile] = []

        for tile in self.offgrid_background:
            if camera_rect.colliderect(tile.grid_rect):
                tiles.append(tile)

        x_range: IntRange = (camera_tile_pos[0] - self.ongrid_padding,
                             1 + camera_bound_tile_pos[0] + self.ongrid_padding)
        y_range: IntRange = (camera_tile_pos[1] - self.ongrid_padding,
                             1 + camera_bound_tile_pos[1] + self.ongrid_padding)

        for x in range(x_range[0], x_range[1]):
            for y in range(y_range[0], y_range[1]):
                check_position: TilePosition = (x, y)

                if check_position in self.tiles:
                    tiles.append(self.tiles[check_position])

        for tile in self.offgrid_foreground:
            if camera_rect.colliderect(tile.grid_rect):
                tiles.append(tile)

        return tiles

    # optimizable 9points -> 4points, raymarching optimization to choose nearest tiles by size
    def tiles_around(self, position: WorldPosition, size: float) -> list[Tile]:
        if not self.active:
            return []

        grid_pos: GridPosition = self.position_world_to_grid(position)
        fixed_pos: GridPosition = grid_pos - (0.5 * Vector2(size, size))
        pos_rect: pygame.FRect = pygame.FRect(*fixed_pos, size, size)
        tile_pos: TilePosition = self.position_grid_to_tile(grid_pos)

        tiles: list[Tile] = []
        scan_size: int = int(size // self.tile_size) + 1

        for tile in self.offgrid_background:
            if pos_rect.colliderect(tile.grid_rect):
                tiles.append(tile)

        x_range: IntRange = (tile_pos[0] - scan_size - self.ongrid_padding,
                             tile_pos[0] + scan_size + 1 + self.ongrid_padding)
        y_range: IntRange = (tile_pos[1] - scan_size - self.ongrid_padding,
                             tile_pos[1] + scan_size + 1 + self.ongrid_padding)

        for x in range(x_range[0], x_range[1]):
            for y in range(y_range[0], y_range[1]):
                check_position: TilePosition = (x, y)

                if check_position in self.tiles:
                    tiles.append(self.tiles[check_position])

        for tile in self.offgrid_foreground:
            if pos_rect.colliderect(tile.grid_rect):
                tiles.append(tile)

        return tiles

    def physical_objects_around(self, position: WorldPosition, size: float) -> list[Tile]:
        if not self.physical:
            return []

        tiles: list[Tile] = self.tiles_around(position, size)

        return tiles

    def get_ongrid_tile(self, tile_position: TilePosition) -> Tile | None:
        if tile_position not in self.tiles:
            return None

        return self.tiles[tile_position]

    def remove_ongrid_at(self, tile_position: TilePosition) -> Tile|None:
        if tile_position not in self.tiles:
            return None

        tile = self.tiles[tile_position]
        del self.tiles[tile_position]

        return tile

    def has_tile(self, tile: Tile) -> bool:
        if tile in self.offgrid_background:
            return True

        if tile in self.offgrid_foreground:
            return True

        if tile.position in self.tiles and self.tiles[tile.position] == tile:
            return True

        return False

    # returns True if no overlap in self.tiles else False
    def add_tile(self, tile: Tile, overwrite: bool=False, offgrid_background: bool=True) -> bool:
        no_overlap: bool = True

        if tile.offgrid and offgrid_background:
            self.offgrid_background.add(tile)

        elif tile.offgrid and not offgrid_background:
            self.offgrid_foreground.add(tile)

        else:
            assert type(tile.position) == TilePosition

            if tile.position in self.tiles:
                no_overlap = False

            if no_overlap or overwrite:
                self.tiles[tile.position] = tile

        return no_overlap

    # returns True if said tile was found and removed else False
    def remove_tile(self, tile: Tile, remove_from_tile_groups: bool=False) -> bool:
        found_and_removed: bool = False

        if tile.offgrid:
            if tile in self.offgrid_background:
                self.offgrid_background.remove(tile)
                found_and_removed = True
            if tile in self.offgrid_foreground:
                self.offgrid_foreground.remove(tile)
                found_and_removed = True
        else:
            assert type(tile.position) == TilePosition

            if tile.position in self.tiles and self.tiles[tile.position] == tile:
                del self.tiles[tile.position]
                found_and_removed = True

        if remove_from_tile_groups:
            found_and_removed = self.tilemap.remove_tile_from_tile_groups(tile) or found_and_removed

        return found_and_removed

    def blit(self) -> None:
        if self.invisible or not self.active:
            return

        # self.game.window.display.fblits(
        #     map(lambda x: x.blit_pair, self.get_onscreen_tiles())
        # )
        for tile in self.get_onscreen_tiles():
            tile.blit()

    def blit_faded(self) -> None:
        if self.invisible or not self.active:
            return

        for tile in self.get_onscreen_tiles():
            tile.blit_faded(self.alpha)
