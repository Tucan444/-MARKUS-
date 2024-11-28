import moderngl
from moderngl import Framebuffer, Texture

from scripts.GameTypes import Viewport


class DoubleFramebuffer:
    def __init__(self, game: 'Game', front: Texture, back: Texture):
        self.game = game
        self.graphics = self.game.graphics
        self.ctx = self.graphics.ctx

        self._front: Texture = front
        self._back: Texture = back
        self._fbo_front: Framebuffer = self.ctx.framebuffer(color_attachments=[self._front])
        self._fbo_back: Framebuffer = self.ctx.framebuffer(color_attachments=[self._back])

        self.write_front: bool=True

    def flip(self) -> None:
        self.write_front = not self.write_front

    def use(self) -> None:
        self.fbo.use()

    def clear(self, r: float, g: float, b: float, a: float=1):
        self._fbo_front.clear(r, g, b, a)
        self._fbo_back.clear(r, g, b, a)

    def release(self) -> None:
        self._fbo_front.release()
        self._fbo_back.release()
        self._front.release()
        self._back.release()

    @property
    def fbo(self) -> Framebuffer:
        return self._fbo_front if self.write_front else self._fbo_back

    @property
    def back(self) -> Texture:
        return self._back if self.write_front else self._front

    @property
    def front(self) -> Texture:
        return self._front if self.write_front else self._back

    @property
    def viewport(self) -> Viewport:
        return self.fbo.viewport

    @viewport.setter
    def viewport(self, new_viewport: Viewport) -> None:
        self._fbo_front.viewport = new_viewport
        self._fbo_back.viewport = new_viewport
