import pygame
from pygame.constants import *
from scripts.GameTypes import SortableFunction, SF_key
from scripts.DataStructures.sorted_array import SortedArray

# suggestion add rebinding
class InputHandler:
    def __init__(self, game: 'Game'):
        self.game: 'Game' = game

        self.on_quit: SortedArray = SortedArray(SortableFunction, key=SF_key)
        self.on_escape_press: SortedArray = SortedArray(SortableFunction, key=SF_key)
        self.on_escape_let: SortedArray = SortedArray(SortableFunction, key=SF_key)

        self.on_mouse_right_press: SortedArray = SortedArray(SortableFunction, key=SF_key)
        self.on_mouse_right_let: SortedArray = SortedArray(SortableFunction, key=SF_key)
        self.on_mouse_left_press: SortedArray = SortedArray(SortableFunction, key=SF_key)
        self.on_mouse_left_let: SortedArray = SortedArray(SortableFunction, key=SF_key)
        self.on_mousewheel_press: SortedArray = SortedArray(SortableFunction, key=SF_key)
        self.on_mousewheel_let: SortedArray = SortedArray(SortableFunction, key=SF_key)
        self.on_mouse_move: SortedArray = SortedArray(SortableFunction, key=SF_key)
        self.on_mouse_scroll_up: SortedArray = SortedArray(SortableFunction, key=SF_key)
        self.on_mouse_scroll_down: SortedArray = SortedArray(SortableFunction, key=SF_key)

        self.on_up_press: SortedArray = SortedArray(SortableFunction, key=SF_key)
        self.on_up_let: SortedArray = SortedArray(SortableFunction, key=SF_key)
        self.on_down_press: SortedArray = SortedArray(SortableFunction, key=SF_key)
        self.on_down_let: SortedArray = SortedArray(SortableFunction, key=SF_key)
        self.on_right_press: SortedArray = SortedArray(SortableFunction, key=SF_key)
        self.on_right_let: SortedArray = SortedArray(SortableFunction, key=SF_key)
        self.on_left_press: SortedArray = SortedArray(SortableFunction, key=SF_key)
        self.on_left_let: SortedArray = SortedArray(SortableFunction, key=SF_key)

        self.on_space_press: SortedArray = SortedArray(SortableFunction, key=SF_key)
        self.on_space_let: SortedArray = SortedArray(SortableFunction, key=SF_key)
        self.on_lshift_press: SortedArray = SortedArray(SortableFunction, key=SF_key)
        self.on_lshift_let: SortedArray = SortedArray(SortableFunction, key=SF_key)
        self.on_tab_press: SortedArray = SortedArray(SortableFunction, key=SF_key)
        self.on_tab_let: SortedArray = SortedArray(SortableFunction, key=SF_key)
        self.on_ctrl_press: SortedArray = SortedArray(SortableFunction, key=SF_key)
        self.on_ctrl_let: SortedArray = SortedArray(SortableFunction, key=SF_key)

    def init(self) -> None:
        pass

    def update(self) -> None:
        for event in pygame.event.get():
            if event.type == QUIT:
                self._call_functions(self.on_quit)

            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    self._call_functions(self.on_mouse_left_press)
                elif event.button == 3:
                    self._call_functions(self.on_mouse_right_press)
                elif event.button == 2:
                    self._call_functions(self.on_mousewheel_press)
                elif event.button == 4:
                    self.game.mouse.mousewheel_position += 1
                    self.game.mouse.last_mousewheel_change = 1
                    self._call_functions(self.on_mouse_scroll_up)
                elif event.button == 5:
                    self.game.mouse.mousewheel_position -= 1
                    self.game.mouse.last_mousewheel_change = -1
                    self._call_functions(self.on_mouse_scroll_down)
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    self._call_functions(self.on_mouse_left_let)
                elif event.button == 3:
                    self._call_functions(self.on_mouse_right_let)
                elif event.button == 2:
                    self._call_functions(self.on_mousewheel_let)
            elif event.type == MOUSEMOTION:
                self._call_functions(self.on_mouse_move)

            elif event.type == KEYDOWN:
                if event.key == K_w:
                    self._call_functions(self.on_up_press)
                elif event.key == K_s:
                    self._call_functions(self.on_down_press)
                elif event.key == K_d:
                    self._call_functions(self.on_right_press)
                elif event.key == K_a:
                    self._call_functions(self.on_left_press)

                elif event.key == K_ESCAPE:
                    self._call_functions(self.on_escape_press)
                elif event.key == K_SPACE:
                    self._call_functions(self.on_space_press)
                elif event.key == K_LSHIFT:
                    self._call_functions(self.on_lshift_press)
                elif event.key == K_TAB:
                    self._call_functions(self.on_tab_press)
                elif event.key == KMOD_CTRL:
                    self._call_functions(self.on_ctrl_press)

            elif event.type == KEYUP:
                if event.key == K_w:
                    self._call_functions(self.on_up_let)
                elif event.key == K_s:
                    self._call_functions(self.on_down_let)
                elif event.key == K_d:
                    self._call_functions(self.on_right_let)
                elif event.key == K_a:
                    self._call_functions(self.on_left_let)

                elif event.key == K_ESCAPE:
                    self._call_functions(self.on_escape_let)
                elif event.key == K_SPACE:
                    self._call_functions(self.on_space_let)
                elif event.key == K_LSHIFT:
                    self._call_functions(self.on_lshift_let)
                elif event.key == K_TAB:
                    self._call_functions(self.on_tab_let)
                elif event.key == KMOD_CTRL:
                    self._call_functions(self.on_ctrl_let)

    def end(self) -> None:
        pass

    @property
    def as_string(self) -> str:
        return ""

    def __repr__(self):
        return self.as_string

    def __str__(self):
        return self.as_string

    def _call_functions(self, functions: SortedArray) -> None:
        self.game.utilities.call_functions(functions)
