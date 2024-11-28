from pygame import Vector2

from scenes.SPECIAL.Effects.Effect import Effect
from scripts.GameTypes import DisplayVector, CommandType
from scripts.Utilities.Graphics.frag import Frag


class GraphicsCommand:
    def __init__(self, game: 'Game', order: float, command_type: CommandType, effect: Effect | None=None,
                 frag: Frag | None=None, display: str= "", alpha: float=1, offset: DisplayVector=None):
        if offset is None:
            offset = Vector2(0, 0)

        self.game: 'Game' = game
        self.order: float = order
        self.command_type: CommandType = command_type

        self.effect: Effect | None = effect
        self.frag: Frag | None = frag
        self.display: str = display
        self.alpha: float = alpha
        self.offset: DisplayVector = offset

        if command_type == CommandType.EFFECT:
            assert self.effect is not None
        elif command_type == CommandType.DISPLAY_BLIT:
            assert self.display != ""
        elif command_type == CommandType.FRAG:
            assert self.frag is not None

    def execute(self):
        if self.command_type == CommandType.EFFECT:
            self.effect.execute()
        elif self.command_type == CommandType.DISPLAY_BLIT:
            self.game.window.blit_display(self.display, alpha=self.alpha, offset=self.offset)
        elif self.command_type == CommandType.FRAG:
            self.frag.execute()

    @property
    def as_string(self) -> str:
        return (f"command type: {self.command_type}, "
                f"effect: {self.effect}, "
                f"frag: {self.frag}, "
                f"display: {self.display}, "
                f"display alpha: {self.alpha}, "
                f"display offset: {self.offset}")

    def __repr__(self):
        return self.as_string

    def __str__(self):
        return self.as_string
