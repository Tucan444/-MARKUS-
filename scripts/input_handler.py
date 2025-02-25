import pygame
from pygame.constants import *
from scripts.GameTypes import SortableFunction, SF_key
from scripts.DataStructures.sorted_array import SortedArray
from scripts.Utilities.action import Action


class InputHandler:
    def __init__(self, game: 'Game'):
        self.game: 'Game' = game

        # pure
        self.anything: Action = Action(self.game, "anything")  # sends event as arg

        self.on_quit: Action = Action(self.game, "on quit")
        self.on_escape_press: Action = Action(self.game, "on escape press")
        self.on_escape_let: Action = Action(self.game, "on escape let")

        self.on_mouse_right_press: Action = Action(self.game, "mouse right press")
        self.on_mouse_right_let: Action = Action(self.game, "mouse right let")
        self.on_mouse_left_press: Action = Action(self.game, "mouse left press")
        self.on_mouse_left_let: Action = Action(self.game, "mouse left let")
        self.on_mousewheel_press: Action = Action(self.game, "mousewheel press")
        self.on_mousewheel_let: Action = Action(self.game, "mousewheel let")
        self.on_mouse_move: Action = Action(self.game, "mouse move")
        self.on_mouse_scroll_up: Action = Action(self.game, "mouse scroll up")
        self.on_mouse_scroll_down: Action = Action(self.game, "mouse scroll down")

        self.on_w_press: Action = Action(self.game, "w press")
        self.on_w_let: Action = Action(self.game, "w let")
        self.on_s_press: Action = Action(self.game, "s press")
        self.on_s_let: Action = Action(self.game, "s let")
        self.on_d_press: Action = Action(self.game, "d press")
        self.on_d_let: Action = Action(self.game, "d let")
        self.on_a_press: Action = Action(self.game, "a press")
        self.on_a_let: Action = Action(self.game, "a let")

        self.on_q_press: Action = Action(self.game, "q press")
        self.on_q_let: Action = Action(self.game, "q let")
        self.on_e_press: Action = Action(self.game, "e press")
        self.on_e_let: Action = Action(self.game, "e let")
        self.on_r_press: Action = Action(self.game, "r press")
        self.on_r_let: Action = Action(self.game, "r let")
        self.on_f_press: Action = Action(self.game, "f press")
        self.on_f_let: Action = Action(self.game, "f let")

        self.on_upA_press: Action = Action(self.game, "upA press")
        self.on_upA_let: Action = Action(self.game, "upA let")
        self.on_downA_press: Action = Action(self.game, "downA press")
        self.on_downA_let: Action = Action(self.game, "downA let")
        self.on_rightA_press: Action = Action(self.game, "rightA press")
        self.on_rightA_let: Action = Action(self.game, "rightA let")
        self.on_leftA_press: Action = Action(self.game, "leftA press")
        self.on_leftA_let: Action = Action(self.game, "leftA let")

        self.on_space_press: Action = Action(self.game, "space press")
        self.on_space_let: Action = Action(self.game, "space let")
        self.on_lshift_press: Action = Action(self.game, "lshift press")
        self.on_lshift_let: Action = Action(self.game, "lshift let")
        self.on_tab_press: Action = Action(self.game, "tab press")
        self.on_tab_let: Action = Action(self.game, "tab let")
        self.on_ctrl_press: Action = Action(self.game, "ctrl press")
        self.on_ctrl_let: Action = Action(self.game, "ctrl let")

        # composite default
        self.on_up_press: Action = Action(self.game, "up press", [self.on_w_press, self.on_upA_press])
        self.on_up_let: Action = Action(self.game, "up let", [self.on_w_let, self.on_upA_let])
        self.on_down_press: Action = Action(self.game, "down press", [self.on_s_press, self.on_downA_press])
        self.on_down_let: Action = Action(self.game, "down let", [self.on_s_let, self.on_downA_let])
        self.on_right_press: Action = Action(self.game, "right press", [self.on_d_press, self.on_rightA_press])
        self.on_right_let: Action = Action(self.game, "right let", [self.on_d_let, self.on_rightA_let])
        self.on_left_press: Action = Action(self.game, "left press", [self.on_a_press, self.on_leftA_press])
        self.on_left_let: Action = Action(self.game, "left let", [self.on_a_let, self.on_leftA_let])

    def init(self) -> None:
        pass

    def update(self) -> None:
        for event in pygame.event.get():
            self.anything.call([event])

            if event.type == QUIT:
                self.on_quit.call()

            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.on_mouse_left_press.call()
                elif event.button == 3:
                    self.on_mouse_right_press.call()
                elif event.button == 2:
                    self.on_mousewheel_press.call()
                elif event.button == 4:
                    self.game.mouse.mousewheel_position += 1
                    self.game.mouse.last_mousewheel_change = 1
                    self.on_mouse_scroll_up.call()
                elif event.button == 5:
                    self.game.mouse.mousewheel_position -= 1
                    self.game.mouse.last_mousewheel_change = -1
                    self.on_mouse_scroll_down.call()
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    self.on_mouse_left_let.call()
                elif event.button == 3:
                    self.on_mouse_right_let.call()
                elif event.button == 2:
                    self.on_mousewheel_let.call()
            elif event.type == MOUSEMOTION:
                self.on_mouse_move.call()

            elif event.type == KEYDOWN:
                if event.key == K_w:
                    self.on_w_press.call()
                elif event.key == K_s:
                    self.on_s_press.call()
                elif event.key == K_d:
                    self.on_d_press.call()
                elif event.key == K_a:
                    self.on_a_press.call()

                elif event.key == K_q:
                    self.on_q_press.call()
                elif event.key == K_e:
                    self.on_e_press.call()
                elif event.key == K_r:
                    self.on_r_press.call()
                elif event.key == K_f:
                    self.on_f_press.call()

                elif event.key == K_UP:
                    self.on_upA_press.call()
                elif event.key == K_DOWN:
                    self.on_downA_press.call()
                elif event.key == K_RIGHT:
                    self.on_rightA_press.call()
                elif event.key == K_LEFT:
                    self.on_leftA_press.call()

                elif event.key == K_ESCAPE:
                    self.on_escape_press.call()
                elif event.key == K_SPACE:
                    self.on_space_press.call()
                elif event.key == K_LSHIFT:
                    self.on_lshift_press.call()
                elif event.key == K_TAB:
                    self.on_tab_press.call()
                elif event.key == K_LCTRL:
                    self.on_ctrl_press.call()

            elif event.type == KEYUP:
                if event.key == K_w:
                    self.on_w_let.call()
                elif event.key == K_s:
                    self.on_s_let.call()
                elif event.key == K_d:
                    self.on_d_let.call()
                elif event.key == K_a:
                    self.on_a_let.call()

                elif event.key == K_q:
                    self.on_q_let.call()
                elif event.key == K_e:
                    self.on_e_let.call()
                elif event.key == K_r:
                    self.on_r_let.call()
                elif event.key == K_f:
                    self.on_f_let.call()

                elif event.key == K_UP:
                    self.on_upA_let.call()
                elif event.key == K_DOWN:
                    self.on_downA_let.call()
                elif event.key == K_RIGHT:
                    self.on_rightA_let.call()
                elif event.key == K_LEFT:
                    self.on_leftA_let.call()

                elif event.key == K_ESCAPE:
                    self.on_escape_let.call()
                elif event.key == K_SPACE:
                    self.on_space_let.call()
                elif event.key == K_LSHIFT:
                    self.on_lshift_let.call()
                elif event.key == K_TAB:
                    self.on_tab_let.call()
                elif event.key == K_LCTRL:
                    self.on_ctrl_let.call()

    def end(self) -> None:
        pass

    @property
    def as_string(self) -> str:
        return ""

    def __repr__(self):
        return self.as_string

    def __str__(self):
        return self.as_string
