import os, sys
import pygame

from scripts.DataStructures.rays import Ray
from scripts.GameTypes import CommandType
from scripts.Utilities.Flow.tick_machine import TickMachine
from scripts.Utilities.Flow.timer import Timer
from scripts.Utilities.Graphics.graphics_command import GraphicsCommand


class Debug:
    def __init__(self, game: 'Game'):
        self.game: 'Game' = game

        self.test_ray: Ray = Ray(pygame.Vector2(200, -100), pygame.Vector2(1, 7))
        self.boilmap = None

        self.g_command: GraphicsCommand = GraphicsCommand(
            self.game, -100, CommandType.DISPLAY_BLIT, display="main", alpha=1)

        # self.timeline3 = Timeline(self.game, "timeline3", 0.3)
        # self.timer = Timer(self.game, "5sec", 5.5, 2.3)
        # self.timer.on_done.add((0, "quack", self.quack_timer))
        # self.game.flow.add_timer(self.timer)
        # print(self.timer)
        #
        # self.tick_machine = TickMachine(self.game, "ticker", 0.5, 1)
        # self.tick_machine.on_tick.add((0, "ticky", self.quack_tick))
        # self.game.flow.add_tick_machine(self.tick_machine)
        # self.tick_machine.tick_time = 0.1

    def init(self) -> None:
        self.game.window.clear_color = (20, 20, 20)
        self.game.window.clear_screen = False
        self.game.inputs.on_escape_press.add((500, "DEBUG END GAME ESCAPE", self.game.end))
        print(f"lines of code writted: {self.project_line_count(False)}")

        self.boilmap = self.game.assets.tilemaps["boilmap"]
        self.primes = self.game.assets.tilemaps["prime true"]
        self.game.window.clear_opengl = False

        self.game.inputs.on_tab_press.add(
            (0, "fullscreen toggle", self.toggle_fullscreen)
        )

        # opengl
        if self.game.graphics.opengl:
            self.game.window.displays["main"] = self.game.window.display_new
            self.game.window.active_display = "main"

    def update(self) -> None:
        self.game.window.set_name(f"fps: {round(self.game.flow.current_fps, 2)}, average fps: {round(self.game.flow.average_fps, 2)}")
        #print(round(self.game.flow.current_fps, 2))
        #print(round(self.game.flow.average_fps, 2))
        # print(f"mem leak - grids: {self.refcount(Grid)}, toggles: {self.refcount(Toggle)}, texts: {self.refcount(Text)}, "
        #       f"gridUI: {self.refcount(GridUI)}, ui_group: {self.refcount(UI_Group)}, images: {self.refcount(Image)}")
        #print(self.game.flow.current_frame)
        #print(self.game.mouse.world_position)

        #self.game.camera.move_camera(pygame.math.Vector2(10 * self.game.flow.dt, -20 * self.game.flow.dt))

        #self.game.assets.tilemaps["TEST TILEMAP"].blit_faded(0.5)

        pygame.draw.circle(self.game.window.display, (0, 255, 0), self.game.mouse.position, 5)
        #print(f"flow: {self.game.flow}, timeline: {self.timeline3}")
        #print(f"flow: {self.game.flow}, timer: {self.timer}")
        #print(f"flow: {self.game.flow}, tick: {self.tick_machine}")

        self.raycast_test()

        if self.game.graphics.opengl:
            self.game.graphics.command_queue.append(self.g_command)

    def end(self) -> None:
        # refs = gc.get_referrers(Toggle)
        #
        # for i, ref in enumerate(refs):
        #     print(f"{i}: {type(ref)}, {ref}")
        pass

    # DEBUG FUNCTIONS START
    def raycast_test(self) -> None:
        pygame.draw.circle(self.game.window.display, (0, 0, 255), self.game.camera.position_world_to_display([0, 0]),
                           30)
        pygame.draw.circle(self.game.window.display, (255, 0, 0),
                           self.game.camera.position_world_to_display([100, 200]), 30)
        self.test_ray.position = self.game.camera.position_display_to_world(self.game.window.display_center)

        eliprect: pygame.FRect = pygame.FRect(-200, -150, 80, 35)
        display_eliprect: pygame.FRect = pygame.FRect(
            *self.game.camera.position_world_to_display(pygame.Vector2(eliprect.left, eliprect.top)), *eliprect.size)
        pygame.draw.ellipse(self.game.window.display, (0, 255, 0), display_eliprect)

        rect: pygame.FRect = pygame.FRect(350, -200, 20, 60)
        pygame.draw.rect(self.game.window.display, (50, 200, 200),
                         pygame.FRect(*self.game.camera.position_world_to_display([350, -200]), 20, 60))

        self.test_ray.direction = self.game.mouse.world_position - self.test_ray.position
        dist1: float = self.test_ray.cast_against_circle(pygame.FRect(-30, -30, 60, 60))
        dist2: float = self.test_ray.cast_against_circle(pygame.FRect(70, 170, 60, 60))
        dist3: float = self.test_ray.cast_against_ellipse(eliprect)
        dist4: float = self.test_ray.cast_against_rect(rect)

        dist5, _ = self.boilmap.raycast(self.test_ray, visualize=False,
                                        physical_only=True, ongrid=True, offgrid=True)#,
                                        #extra_tilemaps=[self.primes])

        dists: list[float] = [dist1, dist2, dist3, dist4, dist5]
        dists = [dist for dist in dists if dist >= 0]
        self.test_ray.blit(self.game, True, ray_length=min(dists) if dists else -1)

    @staticmethod
    def quack_timer(timer: Timer) -> None:
        print(f"quack + {timer.name}")

    @staticmethod
    def quack_tick(tick: TickMachine) -> None:
        print(f"quack + {tick.name} + {tick.ticks_ticked}")

    # DEBUG FUNCTIONS END

    @staticmethod
    def _count_lines_in_file(filepath: str) -> int:
        with open(filepath, 'r') as f:
            lines = f.readlines()

        return len(lines)

    def project_line_count(self, print_individual_files: bool=False) -> int:
        line_count: int = 0
        dirs_to_do: set[str] = set()

        for file in os.listdir():
            if "__" in file:
                continue

            if file[-3:] == ".py" or file[-5:] == ".vert" or file[-5:] == ".frag":
                file_line_count: int = self._count_lines_in_file(file)
                line_count += file_line_count

                if print_individual_files:
                    print(f"{file} : {file_line_count}")
            elif "." in file or file == "_trash":
                continue
            else:
                dirs_to_do.add(file)

        to_clear: list[str] = []
        to_add: list[str] = []
        while dirs_to_do:
            to_clear += dirs_to_do

            for dir_ in dirs_to_do:
                for file in os.listdir(dir_):
                    if "__" in file:
                        continue

                    if file[-3:] == ".py" or file[-5:] == ".vert" or file[-5:] == ".frag":
                        file_line_count: int = self._count_lines_in_file(f"{dir_}/{file}")
                        line_count += file_line_count

                        if print_individual_files:
                            print(f"{dir_}/{file} : {file_line_count}")
                    elif "." in file:
                        continue
                    else:
                        to_add.append(f"{dir_}/{file}")

            for item in to_clear:
                dirs_to_do.remove(item)

            for item in to_add:
                dirs_to_do.add(item)

            to_clear = []
            to_add = []

        return line_count

    @staticmethod
    def refcount(type_: type(object)) -> int:
        return sys.getrefcount(type_)

    def toggle_fullscreen(self) -> None:
        self.game.window.toggle_fullscreen()

    @property
    def as_string(self) -> str:
        return ""

    def __repr__(self):
        return self.as_string

    def __str__(self):
        return self.as_string
