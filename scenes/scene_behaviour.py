class SceneBehaviour:
    def __init__(self, game: 'Game', scene: 'Scene', active: bool, order: int):
        self.game: 'Game' = game
        self.scene: 'Scene' = scene
        self._active: bool = active
        self.order: int = order

    @property
    def active(self) -> bool:
        return self._active

    @active.setter
    def active(self, active) -> None:
        if active == self._active:
            return

        if active:
            self._active = True
            self.init()
        else:
            self._active = False
            self.end()

    def init(self) -> None:
        pass

    def update(self) -> None:
        pass

    def end(self) -> None:
        pass

    @property
    def as_string(self) -> str:
        return (f"belongs to scene: {self.scene.group}, "
                f"active: {self.active}, "
                f"order: {self.order}")

    def __repr__(self):
        return self.as_string

    def __str__(self):
        return self.as_string
