import time

from scripts.GameTypes import RealTime, TimelineTime


class Timeline:
    def __init__(self, game: 'Game', name: str, time_speed: float=1, parent: 'Timeline'=None) -> None:
        self.game: 'Game' = game
        self.name: str = name
        self._time_speed: float = time_speed
        self.timeline_start_time: RealTime = time.time()
        self._last_time_speed_change: RealTime = time.time()
        self._accumulated_local_time: TimelineTime = 0

        self.parent: Timeline|None = parent

    @property
    def time_speed(self) -> float:
        return self._time_speed

    @time_speed.setter
    def time_speed(self, new_speed: float) -> None:
        time_pass = time.time() - self._last_time_speed_change
        self._accumulated_local_time += time_pass * self._time_speed

        self._time_speed = new_speed
        self._last_time_speed_change = time.time()

    @classmethod
    def blank(cls, game: 'Game') -> 'Timeline':
        return Timeline(game, "", 1)

    @property
    def as_string(self) -> str:
        return (f"name: {self.name}, "
                f"time speed: {self.time_speed}, "
                f"real time speed: {self.real_time_speed}"
                f"current fps: {round(self.current_fps, 1)}, "
                f"timeline duration: {round(self.timeline_duration, 2)}, "
                f"delta time: {round(self.dt, 3)}, "
                f"delta time normalized: {round(self.dt_normalized, 3)}")

    def __repr__(self):
        return self.as_string

    def __str__(self):
        return self.as_string

    @property
    def real_time_speed(self) -> RealTime:
        if self.parent is None:
            return self.game.flow.time_speed * self.time_speed
        return self.parent.real_time_speed * self.time_speed

    @property
    def dt(self) -> TimelineTime:
        return min(self.dt_raw, self.game.flow.dt_limit)

    @property
    def inv_dt(self) -> TimelineTime:
        return 1 / self.dt if self.dt != 0 else 1_000_000

    @property
    def dt_raw(self) -> TimelineTime:
        if self.parent is None:
            return self.game.flow.dt * self.time_speed
        return self.parent.dt * self.time_speed

    @property
    def inv_dt_raw(self) -> TimelineTime:
        return 1 / self.dt_raw if self.dt_raw != 0 else 1_000_000

    @property
    def dt_normalized(self) -> TimelineTime:
        if self.parent is None:
            return self.game.flow.dt_normalized * self.time_speed
        return self.parent.dt_normalized * self.time_speed

    @property
    def dt_overflow(self) -> bool:
        return self.dt_raw > self.game.flow.dt_limit

    @property
    def current_fps(self) -> TimelineTime:
        if self.dt == 0:
            return -1

        return 1 / self.dt

    @property
    def local_timeline_duration(self) -> TimelineTime:
        self.time_speed = self.time_speed
        return self._accumulated_local_time

    @property
    def timeline_duration(self) -> RealTime:
        return time.time() - self.timeline_start_time

    # returns (element, integral)
    def growth(self, element: float, expansion: float) -> tuple[float, float]:
        return self.game.flow.growth(element, expansion, self.dt)
