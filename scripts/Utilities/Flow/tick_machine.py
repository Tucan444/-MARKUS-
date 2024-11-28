from scripts.DataStructures.sorted_array import SortedArray
from scripts.GameTypes import SF_key, SortableFunction


class TickMachine:
    def __init__(self, game: 'Game', name: str, tps: float, time_speed: float=1):
        self._tps: float = 1
        self._tick_time: float = 1

        self.game: 'Game' = game
        self.name: str = name
        self.tps: float = tps
        self.time_speed: float = time_speed

        self.time_accumulator: float = 0
        self.ticks_ticked: int = 0

        self.on_tick: SortedArray = SortedArray(SortableFunction, key=SF_key)

    @property
    def as_string(self) -> str:
        return (f"name: {self.name}, "
                f"tps: {self.tps}, "
                f"tick time: {self.tick_time}, "
                f"ticks ticked: {self.ticks_ticked}, "
                f"time accumulated: {self.time_accumulator}, "
                f"number of callbacks: {len(self.on_tick)}")

    def __repr__(self):
        return self.as_string

    def __str__(self):
        return self.as_string

    @property
    def tps(self) -> float:
        return self._tps

    @tps.setter
    def tps(self, new_tps: float) -> None:
        self._tps = new_tps
        self._tick_time = 1 / self._tps

    @property
    def tick_time(self) -> float:
        return self._tick_time

    @tick_time.setter
    def tick_time(self, new_tick_time: float) -> None:
        self._tick_time = new_tick_time
        self._tps = 1 / self._tick_time

    def reset(self) -> None:
        self.time_accumulator = 0
        self.ticks_ticked = 0

    def update(self) -> None:
        self.time_accumulator += self.game.flow.dt * self.time_speed

        while self.time_accumulator > self.tick_time:
            self.time_accumulator -= self.tick_time
            self.ticks_ticked += 1
            self.game.utilities.call_functions(self.on_tick, (self,))
