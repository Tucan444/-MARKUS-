from scripts.Utilities.Flow.timeline import Timeline


# abstract class
class Particle:
    def __init__(self, game: 'Game', spawner: 'ParticleSpawner'):
        self.game: 'Game' = game
        self.spawner: 'ParticleSpawner' = spawner

    @property
    def degraded(self) -> bool:
        return False

    def update(self, timeline: Timeline) -> None:
        return

    def blit(self) -> None:
        return
