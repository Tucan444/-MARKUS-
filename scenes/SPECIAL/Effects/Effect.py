from moderngl import Context
from scripts.Utilities.Graphics.frag import Frag


class Effect:
    def __init__(self, frag: Frag, warning: bool=True) -> None:
        self.game: 'Game' = frag.game
        self.graphics: 'Graphics' = frag.graphics
        self.ctx: Context = frag.ctx
        self.frag: Frag = frag

        self.warning: bool = warning

    def init(self) -> None:
        pass

    @property
    def clone(self) -> 'Effect':
        if self.warning:
            raise Exception("CALLING .CLONE - UNIMPLEMENTED")

        effect = Effect(self.frag)
        return effect

    def _update_frag(self) -> None:
        pass

    def _configure_frag(self) -> None:
        pass

    def _execute_frag(self) -> None:
        self.frag.execute()

    def execute(self) -> None:
        self._update_frag()
        self._configure_frag()
        self._execute_frag()
