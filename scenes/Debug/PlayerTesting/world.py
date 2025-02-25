from pygame import Vector2

from scenes.Debug.PlayerTesting.player_controller import PlayerController
from scenes.SPECIAL.Effects.Effect import Effect
from scenes.scene_behaviour import SceneBehaviour
from scripts.AssetClasses.Tilemap.tilemap import Tilemap
from scripts.GameTypes import WorldPosition, CommandType
from scripts.Utilities.Camera.screen_loop import ScreenLoop
from scripts.Utilities.Flow.timeline import Timeline
from scripts.Utilities.Graphics.graphics_command import GraphicsCommand
from scripts.Utilities.Particles.ParticleTypes.circle_particle import CircleParticle
from scripts.Utilities.Particles.particle_spawner import ParticleSpawner
from scripts.Utilities.Particles.particle_system import ParticleSystem
from scripts.Utilities.physics_entity import PhysicsEntity


class World(SceneBehaviour):
    def __init__(self, game, scene, active, order):
        super().__init__(game, scene, active, order)

        self.tilemap_name: str = "boilmap"
        self.prime_map_name: str = "prime true"

        self.tilemap: Tilemap | None = None
        self.prime_map = None
        self.testmap = None

        self.player_timeline = Timeline(self.game, "player timeline", 1.5)
        self.player: PhysicsEntity | None = PhysicsEntity(game, "player", Vector2(),
                                                          (32, 32), True,
                                                          timeline=self.player_timeline)
        self.player.decay = 0.5
        self.player_controller: None | PlayerController = None

        self.screenshaker = None
        self.screen_loop: ScreenLoop = ScreenLoop(self.game, self.game.assets.images["random/cloud"],
                                                  Vector2(1000, 200), depth_range=Vector2(1, 50),
                                                  timeline=Timeline(self.game, "loop", 1))

        self.particle_system: ParticleSystem = ParticleSystem(self.game, 1_000)
        self.spawner: ParticleSpawner = ParticleSpawner(self.game, self.particle_system,
                                                        Vector2(100, -50), 2.2, Vector2(2, -1),
                                                        Timeline(self.game, "csp", 1))

    def init(self):
        self.tilemap = self.game.assets.tilemaps[self.tilemap_name]
        self.prime_map = self.game.assets.tilemaps[self.prime_map_name]

        self.testmap = self.tilemap.clone
        self.testmap.position = Vector2(100, 100)
        self.testmap.alpha = 0.6

        self.player.obstacles.add(self.tilemap)
        #self.player.obstacles.add(self.prime_map)

        self.player_controller = PlayerController(self)
        self.game.camera.follow_target = True
        self.game.camera.follow_smoothly = True
        self.game.camera.follow_speed = 2
        self.game.camera.get_target_position = self.get_player_position

        self.game.camera.shake(duration=1, softener=2, time_decay=0, shakes_per_second=500, magnitude=500)
        self.player.gravity = Vector2(100, 1000)

        self.screen_loop.generate_loop_images(200)
        self.spawner.spawn_particles(200, CircleParticle)

    def update(self):
        self.screen_loop.update_movement()
        self.screen_loop.blit()
        #self.prime_map.blit()

        self.tilemap.blit()
        self.tilemap.update_animations()

        self.particle_system.update()
        self.particle_system.blit()
        self.spawner.spawn_particles(200, CircleParticle)
        #print(self.particle_system.total_particle_count)

        #self.player.render()
        self.player.update(movement=self.player_controller.movement, blit_site=True)
        self.player.render()

    def end(self):
        self.game.camera.follow_target = False

    def get_player_position(self) -> WorldPosition:
        return self.player.position
