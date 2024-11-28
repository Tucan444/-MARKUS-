from scenes.scene_behaviour import SceneBehaviour

class B(SceneBehaviour):
    def __init__(self, game, scene, active, order):
        super().__init__(game, scene, active, order)
        self.name = "B"

    def init(self):
        print(f"{self.name} inited")

    def update(self):
        print(f"{self.name} updated")

    def end(self):
        print(f"{self.name} ended")

class E:
    def __init__(self):
        pass