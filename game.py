import sys

import pygame
from scripts.GameTypes import *
from scripts.graphics import Graphics

from scripts.utilities import Utilities
from scripts.flow import Flow
from scripts.window import Window
from scripts.mouse import Mouse
from scripts.input_handler import InputHandler
from scripts.assets import Assets
from scripts.camera import Camera
from scripts.scene_manager import SceneManager

from scripts.debug import Debug

class Game:
    def __init__(self, display_size: Resolution, name: str,
                 icon:pygame.Surface | None=None, fullscreen: bool=True,
                 cursor_visible: bool=True, frame_rate:int=60, opengl: bool=False,
                 clear_display: bool=True):
        pygame.mixer.pre_init(48000, -16, 2, 512)
        pygame.init()
        pygame.mixer.set_num_channels(16)

        self.utilities: Utilities = Utilities(self)
        self.flow: Flow = Flow(self, frame_rate)
        self.window: Window = Window(self, display_size, name, icon, fullscreen, opengl, clear_display)
        self.graphics: Graphics = Graphics(self)
        self.mouse: Mouse = Mouse(self, cursor_visible=cursor_visible)
        self.inputs: InputHandler = InputHandler(self)
        self.assets: Assets = Assets(self)
        self.camera: Camera = Camera(self)
        self.scene_manager: SceneManager = SceneManager(self)

        self.debug: Debug = Debug(self)

        self.alive = False
        self._on_quit_funka: SortableFunction = (
            5000, "GAME END", self.end
        )

    def _init(self, *_):
        self.alive = True
        self.inputs.on_quit.add(self._on_quit_funka)

        self._init_components()

    def run(self, *_):
        self._init()

        while self.alive:
            self._update_components()

    def end(self, *_):
        self._end_components()

        pygame.quit()
        sys.exit()

    @property
    def as_string(self) -> str:
        return f"alive: {self.alive}"

    def __repr__(self):
        return self.as_string

    def __str__(self):
        return self.as_string

    def _init_components(self):
        self.utilities.init()
        self.flow.init()
        self.graphics.init()
        self.window.init()
        self.mouse.init()
        self.inputs.init()
        self.assets.init()
        self.camera.init()
        self.scene_manager.init()

        self.debug.init()

    def _update_components(self):
        self.utilities.update()
        self.flow.update()
        self.graphics.update()
        self.window.update()
        self.mouse.update()
        self.inputs.update()
        self.assets.update()
        self.camera.update()
        self.scene_manager.update()

        self.debug.update()

    def _end_components(self):
        self.utilities.end()
        self.flow.end()
        self.graphics.end()
        self.window.end()
        self.mouse.end()
        self.inputs.end()
        self.assets.end()
        self.camera.end()
        self.scene_manager.end()

        self.debug.end()



if __name__ == '__main__':
    # tilemap editor
    game = Game( (1440, 810), "Testing", fullscreen=False, cursor_visible=False,
                 frame_rate=1000, opengl=True, clear_display=True)
    #game.window.clear_display = False

    #game = Game((1440, 810), "Testing", fullscreen=False, cursor_visible=False, frame_rate=1000)

    game.run()
