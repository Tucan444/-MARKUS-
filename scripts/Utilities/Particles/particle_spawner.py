from pygame import Vector2
from scripts.GameTypes import WorldPosition, WorldVector
from scripts.Utilities.Flow.timeline import Timeline
from scripts.Utilities.Particles.particle import Particle


class ParticleSpawner:
    def __init__(self, game: 'Game', particle_system: 'ParticleSystem', position: WorldPosition=None, size: float=1,
                 direction: WorldVector=None, timeline: Timeline=None):
        self._particle_system = None

        self.game: 'Game' = game
        self.particle_system: 'ParticleSystem' = particle_system
        self.position: WorldPosition = position if position is not None else Vector2()
        self.size: float = size
        self.direction: WorldVector = direction
        self.timeline: Timeline = timeline if timeline is not None else Timeline.blank(self.game)

        self.particles: set[Particle] = set()

    @property
    def particle_system(self) -> 'ParticleSystem':
        return self._particle_system

    @particle_system.setter
    def particle_system(self, particle_system: 'ParticleSystem') -> None:
        if self._particle_system is not None:
            self._particle_system.spawners.remove(self)

        self._particle_system = particle_system

        if self._particle_system is not None:
            self._particle_system.spawners.add(self)

    def __del__(self):
        if self.particle_system is not None and self in self.particle_system.spawners:
            self.particle_system.spawners.remove(self)

    def poly_update(self) -> None:
        pass

    def spawn_on_update(self) -> None:
        pass

    def update_particles(self) -> None:
        degraded_particles: list[Particle] = []

        for particle in self.particles:
            particle.update(self.timeline)

            if particle.degraded:
                degraded_particles.append(particle)

        if self.particle_system is not None:
            self.particle_system.particle_count -= len(degraded_particles)

        for particle in degraded_particles:
            self.particles.remove(particle)

    def update(self) -> None:
        self.poly_update()
        self.spawn_on_update()
        self.update_particles()

    def blit(self) -> None:
        for particle in self.particles:
            particle.blit()

    def spawn_particles(self, n: int, particle_class: type(Particle)) -> None:
        if self.particle_system is not None:
            if not self.particle_system.can_spawn_do(n):
                return

        for _ in range(n):
            particle: Particle = particle_class(self.game, self)
            self.particles.add(particle)
