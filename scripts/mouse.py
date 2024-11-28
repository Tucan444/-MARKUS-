import pygame
from scripts.GameTypes import Position, DisplayPosition, WorldPosition, PixelPos_2_Position, DisplayVector

# suggestion fast mouse position
class Mouse:
    def __init__(self, game: 'Game', cursor_visible: bool):
        self.game: 'Game' = game
        self._position: DisplayPosition = pygame.math.Vector2(0, 0)
        self.delta: DisplayVector = pygame.math.Vector2(0, 0)
        self._cursor_visible: bool = cursor_visible

        self.mousewheel_position: int = 0
        self.last_mousewheel_change: int = 0

        pygame.mouse.set_visible(self._cursor_visible)

    def init(self) -> None:
        self.update()

    def update(self) -> None:
        x, y = pygame.mouse.get_pos()
        self.position: DisplayPosition = pygame.math.Vector2(x, y)

    def end(self) -> None:
        pass

    @property
    def as_string(self) -> str:
        return (f"position: {self.position},"
                f" mousewheel position: {self.mousewheel_position},"
                f" last mousewheel change: {self.last_mousewheel_change},"
                f" cursor visible: {self.cursor_visible}")

    def __repr__(self):
        return self.as_string

    def __str__(self):
        return self.as_string

    @property
    def cursor_visible(self) -> bool:
        return self._cursor_visible

    @cursor_visible.setter
    def cursor_visible(self, cursor_visible: bool) -> None:
        self._cursor_visible = cursor_visible
        pygame.mouse.set_visible(self._cursor_visible)

    @property
    def position(self) -> DisplayPosition:
        return self._position

    @position.setter
    def position(self, position: Position) -> None:
        old_position: DisplayPosition = self._position

        self._position = position - self.game.window.dp
        self._position *= self.game.window.display_scalar

        self.delta = self._position - old_position

    @property
    def world_position(self) -> WorldPosition:
        return self.game.camera.position_display_to_world(self._position)
