import random

import pygame.draw
from pygame import Vector2

from scripts.GameTypes import WorldPosition, WorldVector, DisplayPosition
from scripts.Utilities.Flow.timeline import Timeline
from scripts.Utilities.Particles.particle import Particle
from scripts.Utilities.Particles.particle_spawner import ParticleSpawner


class CircleParticle(Particle):
    def __init__(self, game: 'Game', spawner: ParticleSpawner):
        super().__init__(game, spawner)

        self.position: WorldPosition = Vector2(*self.spawner.position)
        self.size: float = self.spawner.size * 5
        self.direction: WorldVector = Vector2(self.spawner.direction) + Vector2(random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5))
        self.direction *= 40

        self.color = (
            100 + random.randint(0, 150), 100 + random.randint(0, 150), 100 + random.randint(0, 150)
        )

    @property
    def display_position(self) -> DisplayPosition:
        return self.game.camera.position_world_to_display(self.position)

    @property
    def degraded(self) -> bool:
        return self.size <= 0

    def update(self, timeline: Timeline) -> None:
        self.size -= timeline.dt
        self.position += self.direction * timeline.dt

    def blit(self) -> None:
        pygame.draw.circle(self.game.window.display, self.color, self.display_position, self.size)
