import random

from pygame import Vector2

from scripts.GameTypes import WorldVector
from scripts.Utilities.Flow.tick_machine import TickMachine
from scripts.Utilities.Flow.timer import Timer

class Screenshaker:
    def __init__(self, game: 'Game', magnitude: float=100, duration: float=1,
                 softener: float=0, time_decay: float=0, shakes_per_second: float=20):
        self.game: 'Game' = game
        self.camera: 'Camera' = game.camera
        self.magnitude: float = magnitude
        self.softener: float = softener
        self.time_decay: float = time_decay

        self.timer: Timer = Timer(self.game, "shaky", duration)
        self.timer.on_done.add((0, "stop shakes", self._stop_shaking))

        self.tick_machine: TickMachine = TickMachine(self.game, "shicker", shakes_per_second)
        self.tick_machine.on_tick.add((0, "shakes", self._shake))

        self.last_shake: WorldVector = Vector2()
        self.ended: bool = False

        self._shake(None)

    @property
    def energy(self) -> float:
        return (1 - self.timer.progress) ** self.softener

    @property
    def time_speed(self) -> float:
        return (1 - self.timer.progress) ** self.time_decay

    def reset(self) -> None:
        self.timer.reset()
        self.tick_machine.reset()

        self.ended = False

    def update(self) -> None:
        if self.ended:
            return

        self.timer.update()
        self.tick_machine.update()

        self.tick_machine.time_speed = self.time_speed

    def _shake(self, _) -> None:
        # suggestion make better random class to use
        new_shake: WorldVector = self.energy * self.magnitude * Vector2(random.random(), random.random())
        self.camera.move_camera(-self.last_shake + new_shake)
        self.last_shake = new_shake

    def _stop_shaking(self, _) -> None:
        self.camera.move_camera(-self.last_shake)
        self.ended = True
