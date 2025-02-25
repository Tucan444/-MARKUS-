import pygame.draw
from pygame import Vector2

from scenes.Debug.PlayerTesting.player_controller import PlayerController
from scenes.SPECIAL.Effects.Effect import Effect
from scenes.SPECIAL.Effects.default.texture_calculator import TextureCalculator
from scenes.scene_behaviour import SceneBehaviour
from scripts.AssetClasses.Tilemap.tilemap import Tilemap
from scripts.GameTypes import WorldPosition, CommandType, ColorNormalized, PrisonShape, OperationType, FloatDoubleFBO
from scripts.Utilities.Camera.screen_loop import ScreenLoop
from scripts.Utilities.Flow.timeline import Timeline
from scripts.Utilities.Graphics.double_framebuffer import DoubleFramebuffer
from scripts.Utilities.Graphics.effect_area import EffectArea
from scripts.Utilities.Graphics.graphics_command import GraphicsCommand
from scripts.Utilities.Graphics.kernel import Kernel
from scripts.Utilities.Graphics.light_gpu import LightGPU
from scripts.Utilities.physics_entity import PhysicsEntity


class Effectorander(SceneBehaviour):
    def __init__(self, game, scene, active, order):
        super().__init__(game, scene, active, order)

        self.box_blur: Effect = None
        self.pixel_transform: Effect = None
        self.linear_transform: Effect = None
        self.convolution: Effect = None
        self.convolution2: Effect = None
        self.wavy: Effect = None
        self.vignette: Effect = None
        self.chroma: Effect = None
        self.grain: Effect = None
        self.fisheye: Effect = None
        self.prison: Effect = None
        self.haze_bloom: Effect = None
        self.sobel_edges: Effect = None
        self.positioned_effect: Effect = None
        self.pe2: Effect = None
        self.pe3: Effect = None
        self.lighting: Effect = None

        self.blur_command: GraphicsCommand = None
        self.pt_command: GraphicsCommand = None
        self.linear_command: GraphicsCommand = None
        self.conv_command: GraphicsCommand = None
        self.conv2_command: GraphicsCommand = None
        self.wavy_command: GraphicsCommand = None
        self.vignette_command: GraphicsCommand = None
        self.chroma_command: GraphicsCommand = None
        self.grain_command: GraphicsCommand = None
        self.fisheye_command: GraphicsCommand = None
        self.prison_command: GraphicsCommand = None
        self.haze_bloom_command: GraphicsCommand = None
        self.sobel_command: GraphicsCommand = None
        self.positioned_effect_command: GraphicsCommand = None
        self.pe2_command: GraphicsCommand = None
        self.pe3_command: GraphicsCommand = None
        self.lighting_command: GraphicsCommand = None

        self.haze_bloom_fbo: DoubleFramebuffer = None
        self.sobel_edge_fbo: FloatDoubleFBO = None
        self.positioning_fbo: DoubleFramebuffer = None
        self.lighting_fbo: FloatDoubleFBO = None

        self.big_effect_edges: EffectArea = None

    def init(self):
        self.box_blur = self.game.graphics.effects["box_blur"].clone
        self.box_blur.blur_size = 3
        self.box_blur.pixel_scale = 1
        self.box_blur.pixel_scaling.y = 1
        self.blur_command = GraphicsCommand(self.game, 5, CommandType.EFFECT, effect=self.box_blur)

        self.pixel_transform = self.game.graphics.effects["pixel_transform"].clone
        #self.pixel_transform.add = (0.2, 0, 0)
        self.pixel_transform.intensity = (1.5, 1.5, 1.5)
        #self.pixel_transform.invert_color = 1
        #self.pixel_transform.grayscale = 0.8
        #self.pixel_transform.dynamic_range = 0.05
        #self.pixel_transform.gamma = 1.3
        self.pixel_transform.hue_shift = 0
        self.pixel_transform.saturation_change = 1
        self.pt_command = GraphicsCommand(self.game, 6, CommandType.EFFECT, effect=self.pixel_transform)

        self.linear_transform = self.game.graphics.effects["linear_transform"].clone
        self.linear_transform.offset = Vector2(200, 50)
        self.linear_transform.scaling = Vector2(0.7, 0.7)
        self.linear_transform.rotate = 0.1
        self.linear_transform.hyper_rotate = 0.1
        self.linear_transform.shear = (Vector2(0.5, 0), True)
        self.linear_command = GraphicsCommand(self.game, 7, CommandType.EFFECT, effect=self.linear_transform)

        self.convolution = self.game.graphics.effects["convolution"].clone
        kernel: Kernel = Kernel(self.game)
        kernel.make_green = True
        kernel.make_blue = True
        kernel.make_red = True
        kernel.become_sobel_v(False)
        self.convolution.kernel = kernel.texture
        self.convolution.kernel_color_range = kernel.color_range
        self.convolution.pixel_scale = 1
        self.convolution.pixel_scaling.y = 1
        self.conv_command = GraphicsCommand(self.game, 8, CommandType.EFFECT, effect=self.convolution)

        self.convolution2 = self.convolution.clone
        kernel2: Kernel = Kernel(self.game)
        kernel2.make_blue = True
        kernel2.make_green = True
        kernel2.make_red = False
        kernel2.become_gauss(5, 3)
        kernel3 = kernel2 @ kernel
        kernel3.save()
        self.convolution2.kernel = kernel3.texture
        self.convolution2.kernel_color_range = kernel3.color_range
        self.conv2_command = GraphicsCommand(self.game, 9, CommandType.EFFECT, effect=self.convolution2)

        self.wavy = self.game.graphics.effects["wavy"].clone
        self.wavy.timeline.time_speed = 2
        self.wavy.x_sine = 0.05
        self.wavy.x_sine_frequency = 10
        self.wavy.y_sine = 0.02
        self.wavy.y_sine_frequency = 5
        self.wavy.twist = 10
        self.wavy.twist_falloff = 20
        self.wavy.twist_position = Vector2(1100, 200)
        self.wavy_command = GraphicsCommand(self.game, 10, CommandType.EFFECT, effect=self.wavy)

        self.vignette = self.game.graphics.effects["vignette"].clone
        self.vignette.vignette_color = (0, 0, 0)
        self.vignette.power = 0.1
        self.vignette_command = GraphicsCommand(self.game, 13**3, CommandType.EFFECT, effect=self.vignette)

        self.chroma = self.game.graphics.effects["chromatic_aberration"].clone
        self.chroma.power = 20
        self.chroma_command = GraphicsCommand(self.game, 12, CommandType.EFFECT, effect=self.chroma)

        self.grain = self.game.graphics.effects["film_grain"].clone
        self.grain.grain_amount = 0.5
        self.grain.grain_color = (1, 0.2, 0.1)
        self.grain_command = GraphicsCommand(self.game, 11, CommandType.EFFECT, effect=self.grain)

        self.fisheye = self.game.graphics.effects["fisheye"].clone
        self.fisheye.zoom = 0.2
        self.fisheye.fisheye_amount = 0.5
        self.fisheye_command = GraphicsCommand(self.game, 14, CommandType.EFFECT, effect=self.fisheye)

        self.prison = self.game.graphics.effects["prison"].clone
        self.prison.obscure_color = (0.4, 0, 0)
        self.prison.obscure = 0.2
        self.prison.obscure_shape = PrisonShape.DIAMOND
        self.prison.bar_color = (0.1, 0, 0)
        self.prison.imprisonment = 0.
        self.prison.bar_shape = PrisonShape.SQUARE
        self.prison.repeatance = 2000
        #self.prison.obscure_last = False
        self.prison_command = GraphicsCommand(self.game, 1, CommandType.EFFECT, effect=self.prison)

        self.haze_bloom_fbo = self.game.graphics.get_display_double_framebuffer()
        self.haze_bloom = self.game.graphics.effects["haze_bloom"].clone
        self.haze_bloom.calculation_target = self.haze_bloom_fbo
        self.haze_bloom.threshold = 0.7
        self.haze_bloom.blur_size = 50
        self.haze_bloom.bloom_color = (1.2, 0.5, 0.1)
        self.haze_bloom.bloom_strength = 1
        self.haze_bloom_command = GraphicsCommand(self.game, 16, CommandType.EFFECT, effect=self.haze_bloom)

        self.sobel_edge_fbo = self.game.graphics.get_display_double_framebuffer(use_floats=True)
        self.sobel_edges = self.game.graphics.effects["sobel_edges"].clone
        self.sobel_edges.calculation_target = self.sobel_edge_fbo
        #self.sobel_edges.grayscale_edges = 0.4
        #self.sobel_edges.edge_operation = OperationType.SUBTRACT
        self.sobel_edges.preblur_pass_size = 3
        self.sobel_edges.edge_strength = 2
        #self.sobel_edges.edge_color = (1, 0.5, 0.2)
        self.sobel_command = GraphicsCommand(self.game, 17, CommandType.EFFECT, effect=self.sobel_edges)

        self.positioning_fbo = self.game.graphics.get_display_double_framebuffer()
        self.positioned_effect = self.game.graphics.effects["positioned_effect"].clone
        self.positioned_effect.calculation_target = self.positioning_fbo
        self.positioned_effect.effect = self.pixel_transform
        self.big_effect_edges = EffectArea(
            self.game, Vector2(600, 400), Vector2(400, 100), 0.1, 0.2, 0, True, False)
        self.positioned_effect.effect_areas.add(self.big_effect_edges)
        self.positioned_effect.effect_areas.add(EffectArea(
            self.game, Vector2(900, -150), Vector2(50, 300), 0.05, 0.08, 2, True, False))
        self.positioned_effect_command = GraphicsCommand(self.game, 18,
                                                         CommandType.EFFECT, effect=self.positioned_effect)

        self.pe2 = self.positioned_effect.clone
        self.pe2.effect = self.pixel_transform
        self.pe2.effect_areas = {
            EffectArea(self.game, Vector2(), Vector2(2000, 10), 0, 0.01, 1),
            EffectArea(self.game, Vector2(-600, -300), Vector2(200, 150), 0.1, 0.01, -1, True)
        }
        self.pe2_command = GraphicsCommand(self.game, 19, CommandType.EFFECT, effect=self.pe2)

        self.pe3 = self.positioned_effect.clone
        self.pe3.effect = self.wavy
        self.pe3.effect_areas = {
            EffectArea(self.game, Vector2(600, -100), Vector2(800, 600), 0.05, 0.2, 0, True, True)
        }
        self.pe3_command = GraphicsCommand(self.game, 19, CommandType.EFFECT, effect=self.pe3)

        self.lighting_fbo = self.game.graphics.get_display_double_framebuffer(True)
        self.lighting = self.game.graphics.effects["lighting"].clone
        self.lighting.calculation_target = self.lighting_fbo
        lights = {
            LightGPU(EffectArea(self.game, Vector2(-292.0, -231.0),Vector2(669.0, 377.0),0, 0.16181818181818183, 1.2363636363636363,True, False),
                     (255, 255, 255), 0.8),
            LightGPU(EffectArea(self.game, Vector2(909.0, 490.0),Vector2(279.0, 68.0),0, 0.2, 2,True, False),
                     (200, 50, 200), 0.9),
            LightGPU(EffectArea(self.game, Vector2(65.0, -531.0),Vector2(0.0, 0.0),0.2, 0.06363636363636364, -2,True, False),
                     (200, 200, 100), 0.4),
            LightGPU(EffectArea(self.game, Vector2(-282.0, -1752.0),Vector2(319.0, 492.0),0.023636363636363636, 0.2, 0.1454545454545455,True, False),
                     (180, 180, 240), 0.7),
LightGPU(EffectArea(self.game, Vector2(-184.0, -229.0),Vector2(268.0, 183.0),0, 0, 0,True, False),
(200, 100, 20), 1.0),
LightGPU(EffectArea(self.game, Vector2(553.0, -393.0),Vector2(366.0, 322.0),0, 0.06, 0,True, False),
(200, 400, 200), 2.0),
LightGPU(EffectArea(self.game, Vector2(-659.0, -376.0),Vector2(0.0, 0.0),0.18727272727272729, 0.11090909090909092, 2,True, False),
(200, 200, 0), 3.0)
        }
        self.lighting.lights = lights
        self.lighting.ambient_color = (0.2, 0.2, 0.2)
        self.lighting_command = GraphicsCommand(self.game, 20, CommandType.EFFECT, effect=self.lighting)

        # opengl
        if self.game.graphics.opengl:
            self.game.window.displays["main"] = self.game.window.display_new
            self.game.window.active_display = "main"

    def update(self):
        self.pixel_transform.hue_shift += self.game.flow.dt * 0.05
        self.linear_transform.rotate += self.game.flow.dt * 0.05
        self.linear_transform.hyper_rotate += self.game.flow.dt * 0.01
        #if self.game.flow.game_run_time > 5:
        #self.prison.obscure += self.game.flow.dt * 0.2
        #self.prison.imprisonment += self.game.flow.dt * 0.4
        #self.wavy.twist += -self.game.flow.dt * 2
        #vig_col: ColorNormalized = self.vignette.vignette_color
        #self.vignette.vignette_color = (vig_col[0], vig_col[1], (vig_col[2] + self.game.flow.dt) % 1)
        self.chroma.focal_point = self.game.mouse.position


        if self.game.graphics.opengl:
            pass
            #self.game.graphics.command_queue.append(self.conv_command)
            #self.game.graphics.command_queue.append(self.conv2_command)
            #self.game.graphics.command_queue.append(self.blur_command)
            self.game.graphics.command_queue.append(self.pt_command)
            #self.game.graphics.command_queue.append(self.linear_command)
            #self.game.graphics.command_queue.append(self.wavy_command)
            #self.game.graphics.command_queue.append(self.vignette_command)
            #self.game.graphics.command_queue.append(self.chroma_command)
            #self.game.graphics.command_queue.append(self.grain_command)
            #self.game.graphics.command_queue.append(self.fisheye_command)
            #self.game.graphics.command_queue.append(self.prison_command)
            #self.game.graphics.command_queue.append(self.haze_bloom_command)
            #self.game.graphics.command_queue.append(self.sobel_command)
            #self.game.graphics.command_queue.append(self.positioned_effect_command)
            #self.game.graphics.command_queue.append(self.pe2_command)
            #self.game.graphics.command_queue.append(self.pe3_command)
            self.game.graphics.command_queue.append(self.lighting_command)
            pass

        #bub = self.big_effect_edges.sdf_display(self.game.mouse.position)
        #pygame.draw.rect(self.game.window.display, (255, 0, 0, 0.5), self.big_effect_edges.display_rect)
        #pygame.draw.circle(self.game.window.display,
        #                   (255 * bub, 255*bub, 255*bub),self.game.mouse.position, 20)

    def end(self):
        self.game.camera.follow_target = False
