import math
import random
from typing import Generator

from pygame import Surface, Vector2

from scripts.DataStructures.sorted_array import SortedArray
from scripts.GameTypes import Range, Resolution, ScreenLoopVector, ScreenLoopPosition
from scripts.Utilities.Camera.screen_loop_image import ScreenLoopImage
from scripts.Utilities.Flow.timeline import Timeline


class ScreenLoop:
    def __init__(self, game: 'Game', image: Surface, velocity: ScreenLoopVector=None, depth_range: Range=None,
                 timeline: Timeline=None, reverse_blit_order: bool=False):
        self.game: 'Game' = game
        self.image: Surface = image
        self.velocity: ScreenLoopVector = velocity if velocity is not None else Vector2()
        self.depth_range: Range = depth_range if depth_range is not None else Vector2(1, 10)
        self.timeline: Timeline = timeline if timeline is not None else Timeline.blank(game)
        self.loop_images: SortedArray = SortedArray(ScreenLoopImage, key=lambda x:-x.depth)
        self.reverse_blit_order: bool = reverse_blit_order

        self.screen_point: Resolution = (
            math.ceil(self.image.get_width() / self.depth_range[0]),
            math.ceil(self.image.get_height() / self.depth_range[0]))

        self.loop_space_size: Resolution = (
            self.screen_point[0] + self.game.window.display_size[0],
            self.screen_point[1] + self.game.window.display_size[1])

    @property
    def as_string(self) -> str:
        return (f"screen point: {self.screen_point}, "
                f"loop space size: {self.loop_space_size}, "
                f"display size: {self.game.window.display_size}, "
                f"number of loop images: {len(self.loop_images)}, "
                f"depth range: {self.depth_range}, "
                f"velocity: {self.velocity}, "
                f"timeline: {self.timeline}")

    def __repr__(self):
        return self.as_string

    def __str__(self):
        return self.as_string

    def create_new_loop_image(self, position: ScreenLoopPosition, depth: float):
        self.loop_images.add(ScreenLoopImage(self.game, self, position, self.image, depth))

    def generate_loop_images(self, n: int):
        for _ in range(n):
            self.loop_images.add(
                ScreenLoopImage(self.game, self,
                                Vector2(random.uniform(0, self.loop_space_size[0]),
                                        random.uniform(0, self.loop_space_size[1])),
                                self.image, random.uniform(self.depth_range.x, self.depth_range.y)))

    def update_movement(self) -> None:
        instant_velocity: ScreenLoopVector = self.velocity * self.timeline.dt

        for loop_image in self.loop_images:
            loop_image.position += instant_velocity * loop_image.depth_inverse
            loop_image.position.x %= self.loop_space_size[0]
            loop_image.position.y %= self.loop_space_size[1]

    def blit(self) -> None:
        image_generator: Generator = self.loop_images.reversed if self.reverse_blit_order else self.loop_images

        for loop_image in image_generator:
            loop_image.blit()
