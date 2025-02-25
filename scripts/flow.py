import math
import time

import pygame

from scripts.GameTypes import Success, WorldTime, RealTime, Time
from scripts.Utilities.Flow.tick_machine import TickMachine
from scripts.Utilities.Flow.timeline import Timeline
from scripts.Utilities.Flow.timer import Timer


# todo add follow like abstraction that can be easily implemented, like follow here, lerp
class Flow:
    def __init__(self, game: 'Game', frame_rate: int, time_speed: float=1):
        self.game: 'Game' = game

        self.frame_rate: int = frame_rate
        self.time_speed: float = time_speed
        self._clock: pygame.time.Clock = pygame.time.Clock()

        self.last_time: RealTime = time.time()
        self.dt_raw: RealTime = 0
        self.dt: WorldTime = 0
        self.dt_normalized: WorldTime = 1
        self.dt_overflow: bool = False
        self.dt_limit: float = 0.1

        self._game_start_time = time.time()
        self.current_frame: int = 0

        self.tick_machines: dict[str, TickMachine] = {}
        self.timers: dict[str, Timer] = {}

    def init(self) -> None:
        self.last_time = time.time()

    def update(self) -> None:
        self._clock.tick(self.frame_rate)

        self.dt_raw = (time.time() - self.last_time)
        self.dt = self.dt_raw * self.time_speed
        self.last_time = time.time()

        if self.dt > self.dt_limit:
            self.dt = self.dt_limit
            self.dt_overflow = True
        else:
            self.dt_overflow = False

        self.dt_normalized = self.dt * self.frame_rate

        self.current_frame += 1

        self._update_tick_machines()
        self._update_timers()

    def _update_tick_machines(self) -> None:
        for tick_machine in self.tick_machines.values():
            tick_machine.update()

    def _update_timers(self) -> None:
        for timer in self.timers.values():
            timer.update()

    def end(self) -> None:
        pass

    @property
    def as_string(self) -> str:
        return (f"fps: {self.frame_rate}, "
                f"current fps: {round(self.current_fps, 1)}, "
                f"game run time: {round(self.game_run_time, 2)}, "
                f"delta time: {round(self.dt, 3)}, "
                f"delta time normalized: {round(self.dt_normalized, 3)}")

    def __repr__(self):
        return self.as_string

    def __str__(self):
        return self.as_string

    # USING REAL TIME
    @property
    def current_fps(self) -> RealTime:
        if self.dt_raw == 0:
            return -1

        return 1 / self.dt_raw

    @property
    def average_dt(self) -> RealTime:
        return (time.time() - self._game_start_time) / self.current_frame

    @property
    def average_fps(self) -> RealTime:
        if self.average_dt == 0:
            return -1

        return 1 / self.average_dt

    @property
    def game_run_time(self) -> RealTime:
        return time.time() - self._game_start_time

    @property
    def timeline_real(self) -> Timeline:
        return Timeline(self.game, "real timeline", 1 / self.time_speed)

    # USING WORLD TIME
    @property
    def timeline(self) -> Timeline:
        return Timeline(self.game, "world timeline", 1)

    @property
    def inv_dt(self) -> WorldTime:
        return 1 / self.dt if self.dt != 0 else 1_000_000

    # optimizable, if needed try with numba
    # returns (element, integral)
    def growth(self, element: float, expansion: float, dt: Time=None) -> tuple[float, float]:
        if dt is None:
            dt = self.dt

        if expansion == 0:
            return element, element * dt

        position = math.log(element) / expansion
        new_position = position + dt

        new_element = math.e ** (new_position * expansion)
        integral = (new_element - element) / expansion

        return new_element, integral

    # OTHER

    def has_tick_machine(self, tick_machine: TickMachine) -> bool:
        return tick_machine.name in self.tick_machines

    def add_tick_machine(self, tick_machine: TickMachine) -> Success:
        if tick_machine.name in self.tick_machines:
            return False

        self.tick_machines[tick_machine.name] = tick_machine

        return True

    def remove_tick_machine(self, tick_machine: TickMachine) -> Success:
        if tick_machine.name not in self.tick_machines:
            return False

        del self.tick_machines[tick_machine.name]

        return True

    def has_timer(self, timer: Timer) -> bool:
        return timer.name in self.timers

    def add_timer(self, timer: Timer) -> Success:
        if timer.name in self.timers:
            return False

        self.timers[timer.name] = timer

        return True

    def remove_timer(self, timer: Timer) -> Success:
        if timer.name not in self.timers:
            return False

        del self.timers[timer.name]

        return True

    def clean_ended_timers(self) -> None:
        for timer_name in list(self.timers.keys()):
            if self.timers[timer_name].ended:
                del self.timers[timer_name]
