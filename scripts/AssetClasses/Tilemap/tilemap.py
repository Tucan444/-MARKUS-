import json
from heapq import heapify, heappush, heappop
import pygame
from scripts.AssetClasses.Tilemap.grid import Grid
from scripts.AssetClasses.Tilemap.gridcaster import Gridcaster
from scripts.AssetClasses.Tilemap.Tiles.tile import Tile
from scripts.AssetClasses.Animation.animation import Animation
from scripts.GameTypes import WorldPosition, Percentage, FocusedPosition, DisplayPosition, TileHitInfo, WorldRay, \
    TilePosition


class Tilemap:
    def __init__(self, game: 'Game', name: str, filepath: str, standard_tile_size: int,
                 position: WorldPosition, alpha: Percentage):
        self.game: 'Game' = game
        self.name: str = name
        self.filepath: str = filepath
        self.standard_tile_size: int = standard_tile_size
        self.position: WorldPosition = position
        self.alpha: Percentage = alpha

        self.grids: dict[str, Grid] = {}
        self.grids_ordered: list[Grid] = []

        self.tilemap_resized_images: dict[int, dict[str, pygame.Surface]] = {}
        self.resized_image_names: dict[int, dict[pygame.Surface, str]] = {}

        self.tilemap_resized_animations: dict[int, dict[str, Animation]] = {}
        self.resized_animation_names: dict[int, dict[Animation, str]] = {}

        self.tilemap_cloned_animations: dict[str, Animation] = {}
        self.tilemap_cloned_names: dict[Animation, str] = {}

        self.tile_groups: dict[str, set[Tile]] = {}

    @property
    def display_position(self) -> DisplayPosition:
        return self.game.camera.position_world_to_display(self.position)

    @property
    def focused_position(self) -> FocusedPosition:
        return self.game.camera.position_world_to_focused(self.position)

    @property
    def tile_count(self) -> int:
        return sum([
            grid.tile_count for grid in self.grids_ordered
        ])

    def clone_animation_for_tilemap(self, animation_name: str) -> bool:
        if animation_name not in self.game.assets.animations:
            return False

        if animation_name in self.tilemap_cloned_animations:
            return True

        anim: Animation = self.game.assets.animations[animation_name].hard_clone
        self.tilemap_cloned_animations[animation_name] = anim
        self.tilemap_cloned_names[anim] = animation_name

        return True

    def get_cloned_animation(self, animation_name: str) -> Animation:
        return self.tilemap_cloned_animations[animation_name]

    def has_grid(self, grid: Grid) -> bool:
        return grid.name in self.grids and self.grids[grid.name] == grid

    def add_grid(self, grid: Grid) -> bool:
        if grid.name in self.grids:
            return False

        self.grids[grid.name] = grid
        self.grids_ordered.append(grid)
        self.grids_ordered.sort(key= lambda x: x.layer)

        return True

    def remove_grid(self, grid: Grid) -> bool:
        if grid.name not in self.grids:
            return False

        del self.grids[grid.name]
        self.grids_ordered.remove(grid)

        return True

    def get_ongrid_tile(self, tile_position: TilePosition) -> set[Tile]:
        tiles: set[Tile] = set()

        for grid in self.grids_ordered:
            tile = grid.get_ongrid_tile(tile_position)

            if tile is None:
                continue

            tiles.add(tile)

        return tiles

    def remove_ongrid_at(self, tile_position: TilePosition) -> set[Tile]:
        tiles: set[Tile] = set()

        for grid in self.grids_ordered:
            tile = grid.remove_ongrid_at(tile_position)

            if tile is None:
                continue

            tiles.add(tile)

        return tiles

    def has_tile(self, tile: Tile) -> bool:
        for grid in self.grids_ordered:
            if grid.has_tile(tile):
                return True

    def remove_tile(self, tile: Tile) -> bool:
        found_and_removed: bool = False

        for grid in self.grids_ordered:
            if grid.remove_tile(tile):
                found_and_removed = True

        found_and_removed = self.remove_tile_from_tile_groups(tile) or found_and_removed

        return found_and_removed

    def remove_tile_from_tile_groups(self, tile: Tile) -> bool:
        found_and_removed: bool = False

        for group_name in tile.groups:
            if tile in self.tile_groups[group_name]:
                self.tile_groups[group_name].remove(tile)
                found_and_removed = True

        return found_and_removed

    @property
    def clone(self) -> 'Tilemap':
        return self.game.utilities.load_tilemap_from_data(self.as_json, self.filepath, self.game)

    @property
    def as_json(self) -> dict:
        return {
            "name": self.name,
            "standard tile size": self.standard_tile_size,
            "alpha": self.alpha,
            "position": list(self.position),
            "grids": [grid.as_json for grid in self.grids.values()]
        }

    @property
    def as_string(self) -> str:
        return (f"name: {self.name}, "
                f"filepath: {self.filepath}, "
                f"standard tile size: {self.standard_tile_size}, "
                f"number of grids: {len(self.grids_ordered)}, "
                f"number of tiles: {self.tile_count}, "
                f"position: {self.position}, "
                f"alpha: {self.alpha}")

    def __repr__(self):
        return self.as_string

    def __str__(self):
        return self.as_string

    def save(self, compact: bool=True) -> None:
        with open(self.filepath, "w") as f:
            if compact:
                json.dump(self.as_json, f, separators=(',', ':'), indent=None)
            else:
                json.dump(self.as_json, f, indent=4)

    def raycast(self, ray: WorldRay, known_hit: TileHitInfo=(-1, None),
                n_steps: int=10, physical_only: bool=True, visualize: bool=False,
                offgrid: bool=True, ongrid: bool=True, extra_tilemaps: list['Tilemap']=None) -> TileHitInfo:
        if extra_tilemaps is None:
            extra_tilemaps = []

        best_hit: TileHitInfo = known_hit

        if offgrid:
            best_hit = self.raycast_offgrid(ray, known_hit, physical_only)
            for tilemap in extra_tilemaps:
                best_hit = tilemap.raycast_offgrid(ray, best_hit, physical_only)

        if ongrid:
            extra_gridcasters: list[Gridcaster] = [gridcaster for tilemap in extra_tilemaps
                                                   for gridcaster in tilemap.get_gridcasters(ray, best_hit, physical_only)]
            best_hit = self.raycast_ongrid(ray, best_hit, n_steps, visualize, physical_only, extra_gridcasters)

        return best_hit

    def raycast_offgrid(self, ray: WorldRay, known_hit: TileHitInfo=(-1, None), physical_only: bool=True) -> TileHitInfo:
        best_hit: TileHitInfo = known_hit

        for grid in self.grids_ordered:
            if physical_only and not grid.physical:
                continue

            best_hit = grid.raycast_offgrid(ray, best_hit)

        return best_hit

    def raycast_ongrid(self, ray: WorldRay, known_hit: TileHitInfo=(-1, None),
                       n_steps: int=10, visualize: bool=False, physical_only: bool=True,
                       extra_gridcasters: list[Gridcaster]=None) -> TileHitInfo:
        if extra_gridcasters is None:
            extra_gridcasters = []

        best_hit: TileHitInfo = known_hit
        gridcasters: list[Gridcaster] = self.get_gridcasters(ray, best_hit, physical_only)
        for gridcaster in extra_gridcasters:
            gridcasters.append(gridcaster)

        for gridcaster in gridcasters:
            gridcaster.init(visualize)
            gridcaster.update_best_hit(best_hit, False)

            if gridcaster.n_steps(n_steps, visualize):
                best_hit = gridcaster.best_hit

        gridcasters = [gridcaster for gridcaster in gridcasters if not gridcaster.done]
        heapify(gridcasters)

        while gridcasters:
            gridcaster: Gridcaster = heappop(gridcasters)
            gridcaster.update_best_hit(best_hit, False)

            if gridcaster.n_steps(n_steps, visualize):
                best_hit = gridcaster.best_hit
            else:
                heappush(gridcasters, gridcaster)

        return best_hit

    def get_gridcasters(self, ray: WorldRay, known_hit: TileHitInfo=(-1, None),
                        physical_only: bool=True) -> list[Gridcaster]:
        gridcasters: list[Gridcaster] = [
            grid.get_gridcaster(ray, known_hit) for grid in self.grids_ordered if not physical_only or grid.physical
        ]

        return gridcasters

    def tiles_around(self, position: WorldPosition, size: float) -> list[Tile]:
        tiles: list[Tile] = []

        for grid in self.grids_ordered:
            tiles += grid.tiles_around(position, size)

        return tiles

    def physical_objects_around(self, position: WorldPosition, size: float) -> list[Tile]:
        tiles: list[Tile] = []

        for grid in self.grids_ordered:
            if not grid.physical:
                continue

            tiles += grid.tiles_around(position, size)

        return tiles

    def blit(self, bottom_layer: int=None, top_layer: int=None) -> None:
        for grid in self.grids_ordered:

            bottom_check: bool = bottom_layer is not None and grid.layer < bottom_layer
            top_check: bool = top_layer is not None and grid.layer > top_layer

            if bottom_check or top_check:
                continue

            grid.blit()

    def blit_faded(self, bottom_layer: int=None, top_layer: int=None) -> None:
        for grid in self.grids_ordered:

            bottom_check: bool = bottom_layer is not None and grid.layer < bottom_layer
            top_check: bool = top_layer is not None and grid.layer > top_layer

            if bottom_check or top_check:
                continue

            grid.blit_faded()

    def update_animations(self, advance_by_time: bool=True) -> None:
        for tile_size in self.tilemap_resized_animations.keys():
            for animation in self.tilemap_resized_animations[tile_size].values():
                if advance_by_time:
                    animation.update_time()
                else:
                    animation.advance_frame()

        for animation in self.tilemap_cloned_animations.values():
            if advance_by_time:
                animation.update_time()
            else:
                animation.advance_frame()

    def update_animation(self, animation_name: str, advance_by_time: bool=True) -> None:
        for tile_size in self.tilemap_resized_animations.keys():
            if animation_name in self.tilemap_resized_animations[tile_size]:
                if advance_by_time:
                    self.tilemap_resized_animations[tile_size][animation_name].update_time()
                else:
                    self.tilemap_resized_animations[tile_size][animation_name].advance_frame()

        if animation_name in self.tilemap_cloned_animations:
            if advance_by_time:
                self.tilemap_cloned_animations[animation_name].update_time()
            else:
                self.tilemap_cloned_animations[animation_name].advance_frame()
