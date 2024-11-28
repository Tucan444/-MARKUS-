import time

import pygame
from pygame import Vector2, FRect
from pygame.locals import *
from scripts.GameTypes import (Resolution, Color,
                               DisplayPosition, DisplayVector, PixelPos)


class Window:
    def __init__(self, game: 'Game', display_size: Resolution, name: str, icon: pygame.Surface,
                 fullscreen: bool = True, opengl: bool = False, clear_display: bool=True,
                 clear_opengl: bool=False, clear_all: bool=True, active_display: str=""):
        self.game: 'Game' = game
        self.icon: pygame.Surface | None = icon
        self.name: str = name

        self._monitor_size: Resolution = (pygame.display.Info().current_w, pygame.display.Info().current_h)
        self.display_size: Resolution = display_size
        self.aspect_ratio: float = self.display_size[0] / self.display_size[1]
        self.aspect_ratio_inverse: float = 1 / self.aspect_ratio
        self.display_center: DisplayPosition = pygame.Vector2(*self.display_size) * 0.5
        self.display_rect: FRect = FRect(0, 0, *self.display_size)

        self.blit_size: Resolution = display_size
        self.display_scalar: float = 1
        self.dp: PixelPos = [0, 0]
        self.fullscreen: bool = False

        self._opengl: bool = opengl
        self._display: pygame.Surface = pygame.display.set_mode(self.display_size, flags=self.opengl_flags)
        self.displays: dict[str, pygame.Surface] = {}
        self.active_display: str = active_display

        self.clear_display: bool = clear_display
        self.clear_opengl: bool = clear_opengl
        self.clear_all: bool = clear_all
        self.clear_color: Color = (0, 0, 0)

        if fullscreen:
            self.toggle_fullscreen()

        self.set_name(name)
        if icon is not None:
            self.set_icon(icon)

    def init(self) -> None:
        pass

    def update(self) -> None:
        if not self.opengl:
            pygame.display.update()
        else:
            pygame.display.flip()

        self._handle_clearing_display()

    def end(self) -> None:
        pass

    def _handle_clearing_display(self) -> None:
        if not self.clear_display:
            return

        if self.clear_all:
            self._clear_main_display()
            for surface in self.displays.values():
                surface.fill(self.clear_color)

        else:
            if self.active_display == "":
                self._clear_main_display()
            else:
                self.display.fill(self.clear_color)

    def _clear_main_display(self) -> None:
        if not self.opengl:
            self._display.fill(self.clear_color)
        else:
            self.game.graphics.clear(self.clear_opengl, self.clear_opengl)

    @property
    def opengl(self) -> bool:
        return self._opengl

    @property
    def display(self) -> pygame.Surface:
        if not self.active_display:
            return self._display

        return self.displays[self.active_display]

    @property
    def display_new(self) -> pygame.Surface:
        return pygame.Surface(self.display_size)

    @property
    def opengl_flags(self) -> int:
        if not self.opengl:
            return 0

        return pygame.OPENGL | pygame.DOUBLEBUF

    @property
    def as_string(self) -> str:
        return (f" display: {self.display_size},"
                f" fullscreen: {self.fullscreen}")

    def __repr__(self):
        return self.as_string

    def __str__(self):
        return self.as_string

    def blit_display(self, source_display: str, target_display: str="", offset: DisplayVector=None, alpha: float=1):
        if offset is None:
            offset = Vector2()

        originally_active: str = self.active_display

        self.active_display = source_display
        display_to_blit: pygame.Surface = self.display

        self.active_display = target_display
        if target_display == "" and self.opengl:
            self.game.graphics.blit_surface(
                self.game.graphics.position_display_to_uv(offset),
                display_to_blit,
                alpha
            )
        else:
            self.display.blit(display_to_blit, offset)

        self.active_display = originally_active

    @staticmethod
    def set_name(name: str) -> None:
        pygame.display.set_caption(name)

    @staticmethod
    def set_icon(icon: pygame.Surface) -> None:
        pygame.display.set_icon(icon)

    def _set_windowed(self) -> None:
        self._display: pygame.Surface = pygame.display.set_mode(self.display_size, flags=self.opengl_flags)
        self.blit_size: Resolution = self.display_size
        self.display_scalar: float = 1
        self.dp: PixelPos = [0, 0]

    def _set_fullscreen(self) -> None:
        self._display = pygame.display.set_mode(self.display_size,
                                                flags=self.opengl_flags | pygame.FULLSCREEN | pygame.SCALED)

        monitor_ratio: float = self._monitor_size[0] / self._monitor_size[1]  # >1 if width is bigger
        display_ratio: float = self.display_size[0] / self.display_size[1]  # >1 if width is bigger

        monitor_is_wider: bool = monitor_ratio > display_ratio

        if monitor_is_wider:
            x_padding: float = (monitor_ratio - display_ratio) * 0.5 * (1 / monitor_ratio)
            self.dp = [self._monitor_size[0] * x_padding, 0]

            x_size: int = int(display_ratio * (1 / monitor_ratio) * self._monitor_size[0])
            self.blit_size: Resolution = (
                x_size,
                int(x_size * (1 / display_ratio))
            )

            self.display_scalar = self.display_size[0] / x_size
        else:
            monitor_ratio_y: float = self._monitor_size[1] / self._monitor_size[0]
            display_ratio_y: float = self.display_size[1] / self.display_size[0]

            y_padding: float = (monitor_ratio_y - display_ratio_y) * 0.5 * (1 / monitor_ratio_y)
            self.dp = [0, self._monitor_size[1] * y_padding]

            y_size: int = int(display_ratio_y * (1 / monitor_ratio_y) * self._monitor_size[1])
            self.blit_size: Resolution = (
                int(y_size * display_ratio),
                y_size
            )

            self.display_scalar = self.display_size[1] / y_size

    def toggle_fullscreen(self) -> bool:
        self.fullscreen = not self.fullscreen

        self.refresh()

        return self.fullscreen

    def refresh(self) -> None:
        if not self.fullscreen:
            self._set_windowed()
        else:
            self._set_fullscreen()
