from pygame import Surface

from scripts.AssetClasses.Animation.animation import Animation
from scripts.GameTypes import Resolution
from scripts.Utilities.Flow.timeline import Timeline


class AnimationMachine:
    def  __init__(self, game: 'Game', timeline: Timeline=None):
        self.game: 'Game' = game

        self.selected_state: str = None
        self.states: dict[str, Animation] = {}

        self.global_flip_x: bool = None
        self.global_flip_y: bool = None
        self.timeline: Timeline = timeline

        self.queued_state: str = None
        self.state_change_callback: callable = lambda x: x

    def change_state(self, new_state: str, interrupt: bool) -> None:
        if interrupt:
            self.queued_state = None
            self.selected_state = new_state
            self._setup_new_state()

            self.state_change_callback(self)

        if not interrupt:
            self.queued_state = new_state

    def update(self, update_time: bool=True):
        self._update_queue()

        if update_time:
            self.current_animation.update_time()
        else:
            self.current_animation.advance_frame()

    def _update_queue(self) -> None:
        if self.current_animation.ended:
            self.selected_state = self.queued_state
            self.queued_state = None
            self._setup_new_state()

    def _setup_new_state(self) -> None:
        self.current_animation.reset()

        if self.global_flip_x is not None:
            self.current_animation.flip_x = self.global_flip_x

        if self.global_flip_y is not None:
            self.current_animation.flip_y = self.global_flip_y

        if self.timeline is not None:
            self.current_animation.timeline = self.timeline

    @property
    def current_animation(self) -> Animation:
        return self.states[self.selected_state] if self.selected_state in self.states else None

    @property
    def current_frame(self) -> Surface:
        return self.current_animation.image

    @property
    def current_size(self) -> Resolution:
        return self.current_animation.size

    @property
    def as_string(self) -> str:
        return (f"selected state: {self.selected_state}, "
                f"states: {self.states}, "
                f"global flip x: {self.global_flip_x}, "
                f"global flip y: {self.global_flip_y}, "
                f"queued state: {self.queued_state}, "
                f"state change callback set: {True if self.state_change_callback is not None else False}")

    def __repr__(self):
        return self.as_string

    def __str__(self):
        return self.as_string
