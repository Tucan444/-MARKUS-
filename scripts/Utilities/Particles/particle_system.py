from scripts.Utilities.Particles.particle import Particle


class ParticleSystem:
    def __init__(self, game: 'Game', limit: int=1_000, parent: 'ParticleSystem'=None):
        self._parent = None

        self.game: 'Game' = game
        self.limit: int = limit
        self.parent: ParticleSystem = parent

        self.children: set[ParticleSystem] = set()
        self.spawners: set['ParticleSpawner'] = set()
        self.particle_count: int = 0

    # optimizable instead of doing tree traversal on each .total_particle_count, we could add to count till last parent in increment
    @property
    def total_particle_count(self) -> int:
        total_count = self.particle_count

        for child in self.children:
            total_count += child.total_particle_count

        return total_count

    @property
    def parent(self) -> 'ParticleSystem':
        return self._parent

    @parent.setter
    def parent(self, parent: 'ParticleSystem') -> None:
        if self._parent is not None:
            self._parent.children.remove(self)

        self._parent = parent

        if self._parent is not None:
            self._parent.children.add(self)

    def can_spawn_do(self, n: int) -> bool:
        if self.total_particle_count + n > self.limit:
            return False

        self.particle_count += n
        return True

    def update(self) -> None:
        for spawner in self.spawners:
            spawner.update()

        for child in self.children:
            child.update()

    def blit(self) -> None:
        for spawner in self.spawners:
            spawner.blit()

        for child in self.children:
            child.blit()

if __name__ == '__main__':
    from particle_spawner import ParticleSpawner

    system = ParticleSystem(None, 5000)
    system2 = ParticleSystem(None, 1000, parent=system)

    spawner = ParticleSpawner(None, system2)
    for _ in range(15):
        spawner.spawn_particles(100, Particle)

    spawner2 = ParticleSpawner(None, system)
    for _ in range(5):
        spawner2.spawn_particles(1502, Particle)

