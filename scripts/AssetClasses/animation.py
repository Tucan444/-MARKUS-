import pygame
from scripts.GameTypes import Resolution


# feature add animation machine, to switch between states easily
class Animation:
    def __init__(self, game: 'Game', frames: list[pygame.Surface],
                 name: str, frame_durations: list[float], loop: bool=True, pong: bool=False,
                 flip_x: bool=False, flip_y: bool=False, flipped_generated: bool=False):
        self.game: 'Game' = game
        self.frames: list[pygame.Surface] = frames
        # 0-flip_x 1-flip_y 2-flip_xy
        self.flipped_frames: list[list[pygame.Surface]] = [[], [], []]
        self.name: str = name
        self.frame_durations: list[float] = frame_durations
        self.loop: bool = loop
        self.pong: bool = pong
        self.ended: bool = False

        self.animation_time: float = 0
        self.duration: float = sum(self.frame_durations)

        self.frame_time: float = 0
        self.current_frame: int = 0
        self.frame_direction: int = 1

        assert(len(self.frames) == len(self.frame_durations))

        self._flipped_generated: bool = flipped_generated
        self._flip_x: bool = False
        self._flip_y: bool = False
        self.flip_x: bool = flip_x
        self.flip_y: bool = flip_y

    @property
    def flip_x(self) -> bool:
        return self._flip_x

    @flip_x.setter
    def flip_x(self, flip_x: bool) -> None:
        self._flip_x = flip_x

        if flip_x and not self.flipped_generated:
            self.flipped_generated = True

    @property
    def flip_y(self) -> bool:
        return self._flip_y

    @flip_y.setter
    def flip_y(self, flip_y: bool) -> None:
        self._flip_y = flip_y

        if flip_y and not self.flipped_generated:
            self.flipped_generated = True

    @property
    def flipped_generated(self) -> bool:
        return self._flipped_generated

    @flipped_generated.setter
    def flipped_generated(self, new_value: bool) -> None:
        if new_value != self._flipped_generated:
            if new_value:
                self.generate_flipped()
            else:
                self.flipped_frames = [[], [], []]

        self._flipped_generated = new_value

    def generate_flipped(self) -> None:
        self.flipped_frames[0] = [pygame.transform.flip(frame, True, False) for frame in self.frames]
        self.flipped_frames[1] = [pygame.transform.flip(frame, False, True) for frame in self.frames]
        self.flipped_frames[2] = [pygame.transform.flip(frame, True, True) for frame in self.frames]
        self._flipped_generated = True

    def reset(self) -> None:
        self.animation_time: float = 0
        self.frame_time: float = 0
        self.current_frame: int = 0
        self.ended: bool = False

    def update_time(self) -> None:
        if self.ended:
            return

        self.animation_time += self.game.flow.dt * self.frame_direction

        if self.pong and self.animation_time >= self.duration:
            self.animation_time -= self.animation_time - self.duration
        if self.loop:
            self.animation_time %= self.duration

        self.frame_time += self.game.flow.dt
        while self.frame_time > self.frame_durations[self.current_frame]:
            self.frame_time -= self.frame_durations[self.current_frame]

            self._advance_current_frame()

    def advance_frame(self) -> None:
        if self.ended:
            return

        self.animation_time += self.frame_durations[self.current_frame] - self.frame_time
        self.frame_time = 0

        self._advance_current_frame()

    def _advance_current_frame(self) -> None:
        self.current_frame += self.frame_direction
        if self.current_frame >= len(self.frames) and not self.loop:
            self.ended = True

        if self.pong and self.current_frame == len(self.frames):
            self.current_frame -= 1
            self.frame_direction = -1
        if self.pong and self.current_frame == -1:
            self.current_frame += 1
            self.frame_direction = 1

        self.current_frame %= len(self.frames)

    @property
    def clone(self) -> 'Animation':
        animation: Animation = Animation(self.game, self.frames, self.name, self.frame_durations, self.loop, self.pong,
                                         self.flip_x, self.flip_y, self.flipped_generated)
        if self.flipped_generated:
            animation.flipped_frames = self.flipped_frames

        return animation

    @property
    def hard_clone(self) -> 'Animation':
        animation: Animation = Animation(
            self.game,
            [frame.copy() for frame in self.frames],
            self.name,
            [duration for duration in self.frame_durations],
            self.loop,
            self.pong,
            self.flip_x,
            self.flip_y
        )

        if self.flipped_generated:
            animation.generate_flipped()

        return animation

    @property
    def frames_clone(self) -> list[pygame.Surface]:
        return [frame.copy() for frame in self.frames]

    @property
    def as_string(self) -> str:
        return (f"name: {self.name}, loop: {self.loop}, ended: {self.ended}, "
                f"number of frames: {len(self.frames)}, "
                f"duration: {round(self.duration, 2)},"
                f"flip x: {self.flip_x},"
                f"flip y: {self.flip_y},"
                f"flipped generated: {self.flipped_generated}")

    def __repr__(self):
        return self.as_string

    def __str__(self):
        return self.as_string

    @property
    def image(self) -> pygame.Surface:
        flip_index = (1 if self.flip_x else 0) + (2 if self.flip_y else 0)

        if flip_index == 0:
            return self.frames[self.current_frame]
        else:
            return self.flipped_frames[flip_index-1][self.current_frame]

    @property
    def size(self) -> Resolution:
        if len(self.frames) == 0:
            return 0, 0

        return self.frames[0].get_size()
