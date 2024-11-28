import pygame.transform
from pygame import Surface
from scripts.GameTypes import Resolution, ScreenLoopPosition, DisplayPosition


class ScreenLoopImage:
    def __init__(self, game: 'Game', screen_loop: 'ScreenLoop',
                 position: ScreenLoopPosition, image: Surface, depth: float):
        self._depth: float = 1
        self._depth_inverse: float = 1
        self.blit_image: Surface = image

        self.game: 'Game' = game
        self.screen_loop: 'ScreenLoop' = screen_loop
        self.position: ScreenLoopPosition = position
        self.image: Surface = image
        self.depth: float = depth

    @property
    def depth(self) -> float:
        return self._depth

    @depth.setter
    def depth(self, new_depth: float) -> None:
        assert self.screen_loop.depth_range[0] <= new_depth <= self.screen_loop.depth_range[1]
        assert new_depth > 0

        self._depth = new_depth
        self._depth_inverse = 1 / new_depth

        if new_depth == 1:
            self.blit_image = self.image
        else:
            new_resolution: Resolution = (
                max(1, round(self.image.get_width() / new_depth)),
                max(1, round(self.image.get_height() / new_depth))
            )
            self.blit_image = pygame.transform.scale(self.image, new_resolution)

    @property
    def depth_inverse(self) -> float:
        return self._depth_inverse

    @property
    def display_position(self) -> DisplayPosition:
        return self.position - self.screen_loop.screen_point

    def blit(self) -> None:
        self.game.window.display.blit(self.blit_image, self.display_position)
