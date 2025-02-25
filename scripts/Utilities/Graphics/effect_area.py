import pygame
from pygame import Vector2

from scripts.GameTypes import DisplayPosition, WorldPosition, Subspace, UVN_Vector, UVN_Position, DisplayRect


# suggestion add rotation, in scribble are notes
class EffectArea:
    INV_SQRT2: float = 1 / (2 ** 0.5)

    def __init__(self, game: 'Game', position: DisplayPosition | WorldPosition=None, size: Subspace=None,
                 radius: float=0, falloff: float=0, falloff_speed: float=0, in_world: bool=False,
                 hill_of_peace: bool=False):
        self.game: 'Game' = game
        self.position: DisplayPosition | WorldPosition = position if position is not None else Vector2()
        self.size: Subspace = size if size is not None else Vector2()
        self.radius: float = radius
        self.falloff: float = falloff
        self.falloff_speed: float = falloff_speed
        self.in_world: bool = in_world
        self.hill_of_peace: bool = hill_of_peace

    @property
    def clone(self) -> 'EffectArea':
        return EffectArea(self.game, self.position, self.size, self.radius, self.falloff,
                          self.falloff_speed, self.in_world, self.hill_of_peace)

    @property
    def falloff_inv(self) -> float:
        if self.falloff == 0:
            return 10000

        return 1 / self.falloff

    @property
    def display_rect(self) -> DisplayRect:
        radius_vec: DisplayPosition = self.game.graphics.position_uv_to_display(Vector2(
            self.radius * self.game.window.aspect_ratio_inverse,
            self.radius
        ))
        if self.hill_of_peace:
            radius_vec *= self.INV_SQRT2

        position: DisplayPosition = self.display_position - radius_vec

        total_size: Subspace = self.size.copy()
        total_size += radius_vec * 2

        if self.hill_of_peace:
            return pygame.FRect(*position, *total_size)

        falloff_vec: DisplayPosition = self.game.graphics.position_uv_to_display(Vector2(
            self.falloff * self.game.window.aspect_ratio_inverse,
            self.falloff
        ))
        position -= falloff_vec
        total_size += falloff_vec * 2

        return pygame.FRect(*position, *total_size)

    @property
    def size_uvn(self) -> Subspace:
        uvn_size: Subspace = self.game.graphics.position_display_to_uv(self.size)
        uvn_size.x *= self.game.window.aspect_ratio
        return uvn_size * 0.5

    @property
    def display_position(self) -> DisplayPosition:
        if self.in_world:
            return self.game.camera.position_world_to_display(self.position)

        return self.position

    @property
    def uvn_position(self) -> UVN_Position:
        position: UVN_Position = self.display_position

        position = self.game.graphics.position_display_to_uvn(position)
        return position

    @property
    def shader_attributes(self) -> dict:
        size_uvn: Subspace = self.size_uvn
        uvn_position: UVN_Position = self.uvn_position + size_uvn
        uvn_position.y *= -1

        return {
            "center": uvn_position,
            "size": size_uvn,
            "radius": self.radius,
            "falloff": self.falloff,
            "falloff_inv": self.falloff_inv,
            "falloff_speed": 2 ** -self.falloff_speed,
            "hill_of_peace": 1 if self.hill_of_peace else 0
        }

    def sdf_world(self, position: WorldPosition) -> float:
        return self.sdf_display(self.game.camera.position_world_to_display(position))

    def sdf_display(self, position: DisplayPosition) -> float:
        position = Vector2(*position)

        position -= self.display_position + (self.size * 0.5)
        position = Vector2(abs(position.x), abs(position.y))
        position -= self.size * 0.5
        position = Vector2(max(0., position.x), max(0., position.y))
        position /= self.game.window.display_size[1]

        distance: float = max(0., position.length() - self.radius)
        if distance == 0:
            return 0 if not self.hill_of_peace else 1
        elif self.falloff == 0:
            return 1 if not self.hill_of_peace else 0

        distance *= self.falloff_inv
        distance = min(1., distance)
        distance = distance ** (2 ** -self.falloff_speed)

        if self.hill_of_peace:
            distance = 1 - distance

        return distance

    @property
    def as_string(self) -> str:
        return (f"( in world: {self.in_world}, "
                f"position: {self.position}, "
                f"size: {self.size}, "
                f"radius: {self.radius}, "
                f"falloff: {self.falloff}, "
                f"falloff speed: {self.falloff_speed}, "
                f"hill of peace: {self.hill_of_peace} )")

    def __repr__(self):
        return self.as_string

    def __str__(self):
        return self.as_string
