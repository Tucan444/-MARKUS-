from scenes.scene_behaviour import SceneBehaviour

class Scene:
    def __init__(self, game: 'Game', name: str, active: bool, order: int):
        self.game: 'Game' = game
        self.name: str = name
        self._active: bool = active
        self.order: int = order

        self.objects: dict[str, SceneBehaviour] = {}
        self.objects_ordered: list[SceneBehaviour] = []
        self.classes: dict[str, type(object)] = {}

    @property
    def active(self) -> bool:
        return self._active

    @active.setter
    def active(self, active) -> None:
        if active == self._active:
            return

        self._active = active
        if active:
            self.init()
        else:
            self.end()

    def init(self) -> None:
        for obj_ in self.objects_ordered:
            if obj_.active:
                obj_.init()

    def update(self) -> None:
        for obj_ in self.objects_ordered:
            if obj_.active:
                obj_.update()

    def end(self) -> None:
        for obj_ in self.objects_ordered:
            if obj_.active:
                obj_.end()

    @property
    def as_string(self) -> str:
        return (f"name: {self.name}, active: {self.active}, order: {self.order}, "
                f"number of objects: {len(self.objects_ordered)}, "
                f"number of classes: {len(self.classes)}")

    def __repr__(self):
        return self.as_string

    def __str__(self):
        return self.as_string

