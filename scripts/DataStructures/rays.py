from pygame.math import Vector2, Vector3
import pygame
from math import *


class Ray:
    def __init__(self, position: Vector2, direction: Vector2):
        self._direction: Vector2 = Vector2()
        self._inverse_direction: Vector2 = Vector2()

        self.position: Vector2 = position
        self.direction: Vector2 = direction

    @property
    def clone(self) -> 'Ray':
        return Ray(Vector2(*self.position), Vector2(*self.direction))

    @property
    def as_string(self) -> str:
        return (f"position: {self.position}, "
                f"direction: {self.direction}")

    def __str__(self):
        return self.as_string

    def __repr__(self):
        return self.as_string

    @property
    def direction_angle(self) -> float:
        return atan2(self.direction.y, self.direction.x)

    @property
    def direction(self) -> Vector2:
        return self._direction

    @direction.setter
    def direction(self, new_direction: Vector2) -> None:
        self._direction = new_direction

        if self._direction.x == 0:
            self._direction.x = 0.000_000_01
        if self._direction.y == 0:
            self._direction.y = 0.000_000_01

        if not self._direction.is_normalized():
            self._direction = self._direction.normalize()

        self._inverse_direction = Vector2(
            1 / self._direction.x,
            1 / self._direction.y
        )

    @property
    def inverse_direction(self) -> Vector2:
        return self._inverse_direction

    def travel(self, t: float) -> Vector2:
        return self.position + self.direction * t

    def cast_against_rect(self, rect: pygame.FRect) -> float:
        if rect.collidepoint(self.position):
            return 0

        left_time: float = (rect.left - self.position.x) * self.inverse_direction.x
        right_time: float = (rect.right - self.position.x) * self.inverse_direction.x

        bottom_time: float = (rect.bottom - self.position.y) * self.inverse_direction.y
        top_time: float = (rect.top - self.position.y) * self.inverse_direction.y

        hit_times: set[float] = set()

        if left_time >= 0 and rect.top <= self.travel(left_time).y <= rect.bottom:
            hit_times.add(left_time)
        if right_time >= 0 and rect.top <= self.travel(right_time).y <= rect.bottom:
            hit_times.add(right_time)

        if bottom_time >= 0 and rect.left <= self.travel(bottom_time).x <= rect.right:
            hit_times.add(bottom_time)
        if top_time >= 0 and rect.left <= self.travel(top_time).x <= rect.right:
            hit_times.add(top_time)

        if hit_times:
            return min(hit_times)

        return -1

    def cast_against_circle(self, rect: pygame.FRect) -> float:
        center: Vector2 = Vector2(*rect.center)
        radius: float = rect.width * 0.5
        assert rect.height == rect.width

        forward: Vector2 = center - self.position
        if forward.magnitude_squared() <= radius ** 2:
            return 0

        parallel_length: float = forward.dot(self.direction)
        orthogonal_length: float = (self.travel(parallel_length) - center).length()

        if orthogonal_length > radius:
            return -1

        in_circle_length: float = sin(acos(orthogonal_length / radius)) * radius

        times: set[float] = {parallel_length + in_circle_length * i
                             for i in range(-1, 1, 2) if parallel_length + in_circle_length * i >= 0}

        if times:
            return min(times)

        return -1

    def cast_against_ellipse(self, rect: pygame.FRect) -> float:
        ray: Ray = self.clone
        ray.position -= Vector2(*rect.center)

        direction: Vector2 = ray.direction.copy()
        direction.x *= 2 / rect.width
        direction.y *= 2 / rect.height
        ray.direction = direction

        ray.position.x *= 2 / rect.width
        ray.position.y *= 2 / rect.height

        circle_time: float = ray.cast_against_circle(pygame.FRect(-1, -1, 2, 2))
        if circle_time < 0:
            return -1

        circle_point: Vector2 = ray.travel(circle_time)
        circle_point.x *= rect.width / 2
        circle_point.y *= rect.height / 2
        circle_point += Vector2(*rect.center)
        ellipse_time: float = (circle_point - self.position).length()

        return ellipse_time

    def blit(self, game: 'Game', in_world: bool=False, color=(255, 100, 100),
             size: float=10, ray_length: float=-1):
        blit_position: Vector2 = self.position
        if in_world:
            blit_position = game.camera.position_world_to_display(blit_position)

        pygame.draw.circle(game.window.display, color, blit_position, size)

        ray_size: float = size * 4 if ray_length < 0 else ray_length
        ray_end: Vector2 = blit_position + self.direction * ray_size

        pygame.draw.line(game.window.display, color, blit_position, ray_end, max(1, int(size // 4)))

class Ray3D:
    pass