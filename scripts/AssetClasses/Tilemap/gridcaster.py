import pygame

from scripts.AssetClasses.Tilemap.Tiles.tile import Tile
import math
from pygame import Vector2
from scripts.GameTypes import TileHitInfo, NormalizedGridRay, GridRay, TilePosition, Vector, Subspace, \
    PixelVec, Done


class Gridcaster:
    MAX_CAST_LENGTH: float = 2_500

    def __init__(self, game: 'Game', grid: 'Grid', ray: GridRay,
                best_hit: TileHitInfo=(-1, None)) -> None:
        self.game: 'Game' = game
        self.grid: 'Grid' = grid

        self.ray: NormalizedGridRay = ray.clone
        self.ray.position = self.ray.position / self.grid.tile_size
        self.ray_x: NormalizedGridRay = self.ray.clone
        self.ray_y: NormalizedGridRay = self.ray.clone

        self.ray_angle: float = ray.direction_angle
        self.angle_tan: float = math.tan(self.ray_angle)
        self.angle_cot: float = 1 / self.angle_tan

        if abs(self.ray_angle) >= math.pi * 0.5:
            self.angle_tan *= -1
        if self.ray_angle <= 0:
            self.angle_cot *= -1

        self.ray_tile_position: TilePosition = self.ray_tile(self.ray)
        self.max_cast_length_normed: float = self.MAX_CAST_LENGTH / self.grid.tile_size

        self.best_hit_local: TileHitInfo = (best_hit[0] / grid.tile_size, best_hit[1])

        # optimizable length can be computed in world space, while rays be in normalized space
        self.x_vector: Vector = Vector2()
        self.y_vector: Vector = Vector2()
        self.x_vector_length: float = 0
        self.y_vector_length: float = 0

        self.x_length: float = 0
        self.y_length: float = 0
        self.x_steps: int = 0
        self.y_steps: int = 0

        self.step_directions: PixelVec = [
            1 if self.ray.direction.x > 0 else -1, 1 if self.ray.direction.y > 0 else -1
        ]

        self.x_done: bool = False
        self.y_done: bool = False

    @property
    def as_string(self) -> str:
        return (f"x length: {self.x_length}, "
                f"y length: {self.y_length}, "
                f"x done: {self.x_done}, "
                f"y done: {self.y_done}, "
                f"done: {self.done}")

    def __str__(self):
        return self.as_string

    def __repr__(self):
        return self.as_string

    def __eq__(self, other: 'Gridcaster') -> bool:
        return self.length_covered == other.length_covered

    def __ne__(self, other: 'Gridcaster') -> bool:
        return self.length_covered != other.length_covered

    def __lt__(self, other) -> bool:
        return self.length_covered < other.length_covered

    def __le__(self, other) -> bool:
        return self.length_covered <= other.length_covered

    def __gt__(self, other) -> bool:
        return self.length_covered > other.length_covered

    def __ge__(self, other) -> bool:
        return self.length_covered >= other.length_covered

    @property
    def done(self) -> bool:
        both_done: bool = self.x_done and self.y_done
        y_overshoot: bool = self.x_done and (self.y_length > self.x_length)
        x_overshoot: bool = self.y_done and (self.x_length > self.y_length)
        over_best: bool = (self.y_length > self.best_hit_local[0] >= 0
                           and self.x_length > self.best_hit_local[0])
        return both_done or y_overshoot or x_overshoot or over_best

    @property
    def best_hit(self) -> TileHitInfo:
        return self.best_hit_local[0] * self.grid.tile_size, self.best_hit_local[1]

    @property
    def length_covered(self) -> float:
        return min(self.x_length, self.y_length) * self.grid.tile_size

    @property
    def x_ray_hit(self) -> Tile | None:
        tile_pos: TilePosition = (
            self.ray_tile_position[0] + self.x_steps * self.step_directions[0],
            self.ray_x.position.y // 1
        )

        return self.grid.get_ongrid_tile(tile_pos)

    @property
    def y_ray_hit(self) -> Tile | None:
        tile_pos: TilePosition = (
            self.ray_y.position.x // 1,
            self.ray_tile_position[1] + self.y_steps * self.step_directions[1]
        )

        return self.grid.get_ongrid_tile(tile_pos)

    @staticmethod
    def ray_tile(ray: NormalizedGridRay) -> TilePosition:
        return ray.position.x // 1, ray.position.y // 1

    @staticmethod
    def ray_tile_subspace(ray: NormalizedGridRay) -> Subspace:
        subspace: Subspace = Vector2(0, 0)

        if ray.direction.x > 0:
            subspace.x = 1 - (ray.position.x % 1)
        else:
            subspace.x = ray.position.x % 1

        if ray.direction.y > 0:
            subspace.y = 1 - (ray.position.y % 1)
        else:
            subspace.y = ray.position.y % 1

        return subspace

    def update_best_hit(self, new_hit: TileHitInfo, local_hit: bool=True) -> None:
        if new_hit[0] < 0:
            return

        if not local_hit:
            new_hit = (new_hit[0] / self.grid.tile_size, new_hit[1])

        if self.best_hit_local[0] < 0 or new_hit[0] < self.best_hit_local[0]:
            self.best_hit_local = new_hit

    def init(self, blit_rays: bool=False) -> None:
        intersecting_tile: Tile | None = self.grid.get_ongrid_tile(self.ray_tile_position)
        if intersecting_tile is not None:
            self.x_done = True
            self.y_done = True
            self.best_hit_local = (0, intersecting_tile)
            return

        subspace: Subspace = self.ray_tile_subspace(self.ray_x)

        x_initial_vector: Vector = Vector2(subspace.x * self.step_directions[0], self.angle_tan * subspace.x)
        y_initial_vector: Vector = Vector2(self.angle_cot * subspace.y, subspace.y * self.step_directions[1])

        self.ray_x.position += x_initial_vector
        self.ray_y.position += y_initial_vector

        self.x_length += x_initial_vector.length()
        self.y_length += y_initial_vector.length()

        self.x_steps += 1
        self.y_steps += 1

        x_tile: Tile | None = self.x_ray_hit
        y_tile: Tile | None = self.y_ray_hit

        if x_tile is not None:
            self.x_done = True
            self.update_best_hit((self.x_length, x_tile))
        if y_tile is not None:
            self.y_done = True
            self.update_best_hit((self.y_length, y_tile))

        self.x_vector = Vector2(self.step_directions[0], self.angle_tan)
        self.y_vector = Vector2(self.angle_cot, self.step_directions[1])

        self.x_vector_length = self.x_vector.length()
        self.y_vector_length = self.y_vector.length()

        if blit_rays:
            self.blit_rays()

    def cast(self, blit_steps: bool=False):
        while not self.step():
            if blit_steps:
                self.blit_rays()

        if blit_steps:
            self.blit_rays()

    def n_steps(self, n_steps: int=10, blit_steps: bool=False) -> Done:
        done: bool = False

        for _ in range(n_steps):
            if blit_steps:
                self.blit_rays()

            if self.step():
                done = True
                break

        if blit_steps:
            self.blit_rays()

        return done

    def step(self) -> Done:
        do_x: bool = self.x_length <= self.y_length

        if do_x and not self.x_done:
            self.ray_x.position += self.x_vector
            self.x_length += self.x_vector_length
            self.x_steps += 1

            x_tile: Tile | None = self.x_ray_hit
            if x_tile is not None:
                self.x_done = True
                self.update_best_hit((self.x_length, x_tile))

            if self.x_length > self.max_cast_length_normed:
                self.x_done = True

        elif not self.y_done:
            self.ray_y.position += self.y_vector
            self.y_length += self.y_vector_length
            self.y_steps += 1

            y_tile: Tile | None = self.y_ray_hit
            if y_tile is not None:
                self.y_done = True
                self.update_best_hit((self.y_length, y_tile))

            if self.y_length > self.max_cast_length_normed:
                self.y_done = True

        return self.done

    def blit_rays(self, radius: int=8) -> None:
        ray_pos = self.grid.position_grid_to_display(self.ray.position * self.grid.tile_size)
        pygame.draw.circle(self.game.window.display, (0, 255, 255), ray_pos, radius)

        x_pos = self.grid.position_grid_to_display(self.ray_x.position * self.grid.tile_size)
        pygame.draw.circle(self.game.window.display, (255, 255, 255), x_pos, radius)

        y_pos = self.grid.position_grid_to_display(self.ray_y.position * self.grid.tile_size)
        pygame.draw.circle(self.game.window.display, (255, 0, 255), y_pos, radius)
