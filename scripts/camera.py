from copy import copy
from pygame.math import Vector2
from scripts.GameTypes import (Mutable2, WorldVector, WorldPosition, PixelWorldPos)
from scripts.Utilities.Camera.screenshaker import Screenshaker


class Camera:
    def __init__(self, game: 'Game'):
        self.game: 'Game' = game

        self.position: WorldPosition = -self.game.window.display_center

        self.get_target_position: callable = None
        self.follow_target: bool = False
        self.follow_smoothly: bool = False
        self.follow_speed: float = 1

        self.render_cameraPos: PixelWorldPos = [0, 0]

        self._screenshakers: set[Screenshaker] = set()

    def init(self) -> None:
        self.update()

    def update(self) -> None:
        self._handle_following_target()
        self._update_screenshakers()
        self._update_render_cameraPos()

    def end(self) -> None:
        pass

    @property
    def as_string(self) -> str:
        return (f"scroll: {self.position},"
                f" following target: {self.follow_target},"
                f" following smoothly: {self.follow_smoothly},"
                f" follow speed: {self.follow_speed}")

    def __repr__(self):
        return self.as_string

    def __str__(self):
        return self.as_string

    def _handle_following_target(self) -> None:
        if not self.follow_target:
            return

        target_position: WorldPosition = self.get_target_position()
        desired_position: WorldPosition = Vector2(
            target_position[0] - (self.game.window.display.get_width() * 0.5),
            target_position[1] - (self.game.window.display.get_height() * 0.5)
        )

        if not self.follow_smoothly:
            self.position = desired_position
            return

        scroll_multiplier, _ = self.game.flow.growth(1, -self.follow_speed)
        scroll_multiplier = 1 - scroll_multiplier

        self.position[0] += (desired_position[0] - self.position[0]) * scroll_multiplier
        self.position[1] += (desired_position[1] - self.position[1]) * scroll_multiplier

    def _update_render_cameraPos(self) -> None:
        self.render_cameraPos = [int(self.position[0]), int(self.position[1])]

    def _update_screenshakers(self) -> None:
        to_remove: list[Screenshaker] = []

        for screenshaker in self._screenshakers:
            screenshaker.update()

            if screenshaker.ended:
                to_remove.append(screenshaker)

        for screenshaker in to_remove:
            self._screenshakers.remove(screenshaker)

    def move_camera(self, vector: WorldVector) -> None:
        self.position += vector
        self._update_render_cameraPos()

    def teleport_to_target(self) -> None:
        following_smoothly: bool = self.follow_smoothly
        self.follow_smoothly = False

        self._handle_following_target()
        self.follow_smoothly = following_smoothly

    def shake(self, magnitude: float=100, duration: float=1, softener: float=0,
              time_decay: float=0, shakes_per_second: float=20) -> None:
        screenshaker: Screenshaker = Screenshaker(self.game, magnitude, duration,
                                                  softener, time_decay, shakes_per_second)

        self._screenshakers.add(screenshaker)

    def position_world_to_display(self, position: Mutable2) -> Mutable2:
        position = copy(position)
        position[0] -= self.render_cameraPos[0]
        position[1] -= self.render_cameraPos[1]
        return position

    def position_display_to_world(self, position: Mutable2) -> Mutable2:
        position = copy(position)
        position[0] += self.render_cameraPos[0]
        position[1] += self.render_cameraPos[1]
        return position

    def position_world_to_focused(self, position: Mutable2) -> Mutable2:
        position = copy(position)
        position[0] -= self.render_cameraPos[0] + self.game.window.display_center[0]
        position[1] -= self.render_cameraPos[1] + self.game.window.display_center[1]
        return position

    def position_focused_to_world(self, position: Mutable2) -> Mutable2:
        position = copy(position)
        position[0] += self.render_cameraPos[0] + self.game.window.display_center[0]
        position[1] += self.render_cameraPos[1] + self.game.window.display_center[1]
        return position

    def position_display_to_focused(self, position: Mutable2) -> Mutable2:
        position = copy(position)
        position[0] -= self.game.window.display_center[0]
        position[1] -= self.game.window.display_center[1]
        return position

    def position_focused_to_display(self, position: Mutable2) -> Mutable2:
        position = copy(position)
        position[0] += self.game.window.display_center[0]
        position[1] += self.game.window.display_center[1]
        return position
