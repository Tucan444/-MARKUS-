from scripts.DataStructures.sorted_array import SortedArray
from scripts.GameTypes import Percentage, SortableFunction, SF_key


class Timer:
    def __init__(self, game: 'Game', name: str, duration: float, time_speed: float=1) -> None:
        self.game: 'Game' = game
        self.name: str = name
        self.duration: float = duration
        self.time_speed: float = time_speed
        self.ended: bool = False

        self.accumulated_time: float = 0
        self.on_done: SortedArray = SortedArray(SortableFunction, key=SF_key)

    @property
    def as_string(self) -> str:
        return (f"name: {self.name}, "
                f"duration: {round(self.duration, 3)}, "
                f"time_speed: {round(self.time_speed, 2)}, "
                f"ended: {self.ended}, "
                f"accumulated time: {self.accumulated_time}, "
                f"number of callbacks: {len(self.on_done)}")

    def __repr__(self):
        return self.as_string

    def __str__(self):
        return self.as_string

    @property
    def progress(self) -> Percentage:
        if self.ended:
            return 1

        return self.accumulated_time / self.duration

    def reset(self) -> None:
        self.accumulated_time = 0
        self.ended = False

    def update(self) -> None:
        if self.ended:
            return

        self.accumulated_time += self.game.flow.dt * self.time_speed

        if self.accumulated_time >= self.duration:
            self.ended = True
            self.game.utilities.call_functions(self.on_done, (self,))
