import pygame.draw
from pygame import Vector2, FRect
from scripts.DataStructures.sorted_array import SortedArray
from scripts.GameTypes import WorldPosition, Resolution, DisplayPosition, WorldVector, SortableFunction, SF_key, \
    Subspace, Detected
from scripts.Utilities.Flow.timeline import Timeline


class PhysicsEntity:
    def __init__(self, game: 'Game', name: str, position: WorldPosition, size: Resolution,
                 use_basic_behaviour: bool=True, max_move_size: float=15, timeline: Timeline=None):
        self.game: 'Game' = game
        self.name: name = name
        self.last_frame_position: WorldPosition = position
        self.position: WorldPosition = position
        self.size: Resolution = size
        self.obstacles: set[object] = set()

        self.max_move_size: float = max_move_size
        self.timeline = timeline if timeline is not None else Timeline.blank(game)

        # HOW OBSTACLES WORK
        # all obstacles must contain function .physical_objects_around(position, biggest_side) -> list[object]
        # all objects in the returned list must contain .rect property, rect has to be in world space

        self.decay: float = 0

        self.velocity: WorldVector = Vector2()
        self.frame_velocity: WorldVector = Vector2()
        self.frame_magnitude: float = 0

        self.accelerators: dict[str, WorldVector] = {
            "gravity": Vector2(0, 1000)}
        self.frame_acceleration: WorldVector = Vector2()
        self._applied_acceleration: WorldVector = Vector2()
        self.is_stuck: bool = False

        # these pass in (self, instant_movement, objects_to_check, rects_to_check, site_rect)
        self.invoke_on_movement: SortedArray = SortedArray(SortableFunction, key=SF_key)

        # these pass in (self, [collided objects])
        self.invoke_on_stuck: SortedArray = SortedArray(SortableFunction, key=SF_key)
        self.invoke_on_collide_left: SortedArray = SortedArray(SortableFunction, key=SF_key)
        self.invoke_on_collide_right: SortedArray = SortedArray(SortableFunction, key=SF_key)
        self.invoke_on_collide_top: SortedArray = SortedArray(SortableFunction, key=SF_key)
        self.invoke_on_collide_bottom: SortedArray = SortedArray(SortableFunction, key=SF_key)

        self._basic_stuck_funka: SortableFunction = (0, "basic_stuck", self.basic_stuck)
        self._basic_collide_left_funka: SortableFunction = (0, "basic_collide_left", self.basic_collide_left)
        self._basic_collide_right_funka: SortableFunction = (0, "basic_collide_right", self.basic_collide_right)
        self._basic_collide_top_funka: SortableFunction = (0, "basic_collide_top", self.basic_collide_top)
        self._basic_collide_bottom_funka: SortableFunction = (0, "basic_collide_bottom", self.basic_collide_bottom)

        self._use_basic_behaviour: bool = False
        self.use_basic_behaviour: bool = use_basic_behaviour

    @property
    def acceleration(self) -> WorldVector:
        acceleration: WorldVector = Vector2()
        for vector in self.accelerators.values():
            acceleration += vector

        return acceleration

    @property
    def use_basic_behaviour(self) -> bool:
        return self._use_basic_behaviour

    @use_basic_behaviour.setter
    def use_basic_behaviour(self, use_basic_behaviour: bool) -> None:
        if use_basic_behaviour == self._use_basic_behaviour:
            return

        if use_basic_behaviour:
            self.invoke_on_stuck.add(self._basic_stuck_funka)
            self.invoke_on_collide_left.add(self._basic_collide_left_funka)
            self.invoke_on_collide_right.add(self._basic_collide_right_funka)
            self.invoke_on_collide_top.add(self._basic_collide_top_funka)
            self.invoke_on_collide_bottom.add(self._basic_collide_bottom_funka)
        else:
            self.invoke_on_stuck.remove(self._basic_stuck_funka)
            self.invoke_on_collide_left.remove(self._basic_collide_left_funka)
            self.invoke_on_collide_right.remove(self._basic_collide_right_funka)
            self.invoke_on_collide_top.remove(self._basic_collide_top_funka)
            self.invoke_on_collide_bottom.remove(self._basic_collide_bottom_funka)

        self._use_basic_behaviour = use_basic_behaviour

    @property
    def delta_position(self) -> WorldVector:
        return self.position - self.last_frame_position

    @property
    def center(self) -> WorldPosition:
        return self.position + (0.5 * Vector2(*self.size))

    @property
    def display_center(self) -> DisplayPosition:
        return self.display_position + (0.5 * Vector2(*self.size))

    @property
    def world_rect(self) -> FRect:
        return FRect(*self.position, *self.size)

    @property
    def display_rect(self) -> FRect:
        return FRect(*self.display_position, *self.size)

    @property
    def display_position(self) -> DisplayPosition:
        return self.game.camera.position_world_to_display(self.position)

    @property
    def phys_json(self) -> dict:
        return {
            "class_name": self.__name__,
            "name": self.name,
            "position": list(self.position),
            "size" : self.size,
            "velocity": self.velocity,
            "gravity": self.gravity,
            "is stuck": self.is_stuck
        }

    @property
    def as_json(self) -> dict:
        return self.phys_json

    @property
    def as_string(self) -> str:
        return (f"name: {self.name}, position: {self.position}, velocity: {self.velocity}, "
                f"gravity: {self.gravity}, size: {self.size}, number of obstacles: {len(self.obstacles)}, "
                f"is struck: {self.is_stuck}")

    def __repr__(self):
        return self.as_string

    def __str__(self):
        return self.as_string

    def update(self, movement: WorldVector=None, burst: WorldVector=None, blit_site: bool=False) -> None:
        if movement is None:
            movement = Vector2()
        if burst is None:
            burst = Vector2()

        self._update_forces_start(movement, burst)
        self._update_movement(blit_site)
        self._update_forces_end()

    def _update_forces_start(self, movement: WorldVector, burst: WorldVector) -> None:
        self._update_acceleration_start(burst)
        displacement = self._update_decay()

        self.frame_velocity = movement + (self.velocity.normalize() * displacement * self.timeline.inv_dt)
        self.frame_magnitude = self.frame_velocity.length()

    def _update_forces_end(self) -> None:
        self._update_acceleration_end()

    def render(self) -> None:
        self.game.window.display.blit(self.game.assets.images["random/tile"], self.display_position)
        # debugging turn off later
        #pygame.draw.rect(self.game.window.display, (255, 0, 255), self.display_rect)

    def _update_acceleration_start(self, burst: WorldVector=None) -> None:
        if burst is None:
            burst = Vector2()

        self.frame_acceleration = self.acceleration + burst
        self._applied_acceleration = self.frame_acceleration * 0.5 * self.timeline.dt

        self.velocity += self._applied_acceleration

    def _update_decay(self) -> float:
        velocity_magnitude = self.velocity.length()

        new_magnitude, displacement = self.growth(velocity_magnitude, -self.decay)

        self.velocity = (self.velocity / velocity_magnitude) * new_magnitude

        return displacement

    def growth(self, element: float, expansion: float) -> tuple[float, float]:
        return self.timeline.growth(element, expansion)

    def _update_acceleration_end(self) -> None:
        self.velocity += self._applied_acceleration

    def _update_movement(self, blit_site: bool=False) -> None:
        self.last_frame_position = Vector2(*self.position)
        self.is_stuck: bool = False

        frame_movement: WorldVector = self.frame_velocity * self.timeline.dt
        move_site: Subspace = Vector2(self.size[0] + abs(frame_movement.x), self.size[1] + abs(frame_movement.y))
        site_position: WorldPosition = Vector2(min(self.position.x, self.position.x + frame_movement.x),
                                         min(self.position.y, self.position.y + frame_movement.y))
        site_rect: FRect = FRect(*site_position, *move_site)
        biggest_side: float = max(*move_site)

        center: WorldPosition = self.center
        center_moved: WorldPosition = center + frame_movement * 0.5 # IF BUG ITS PROBABLY HERE, DO IN 2 steps

        objects_to_check: list[object] = [
            obj for obstacle in self.obstacles for obj in obstacle.physical_objects_around(center_moved, biggest_side)
        ]
        rects_to_check: list[FRect] = [
            obj.rect for obj in objects_to_check
        ]

        movement_length = frame_movement.length()
        unit_movement: WorldVector = Vector2()

        if movement_length != 0:
            unit_movement = frame_movement.normalize() * self.max_move_size
        # UNCOMMENT ONLY FOR DEBUG PURPOSE, OR YOUR OWN
        # iterations: int = ((movement_length // self.max_move_size) +
        #                    1 if movement_length % self.max_move_size != 0 else 0)
        # print(iterations)

        self.is_stuck = self._handle_stucking(center, objects_to_check, rects_to_check)

        while movement_length > 0:
            instant_movement: WorldVector = unit_movement if movement_length > self.max_move_size else frame_movement

            self.game.utilities.call_functions(
                self.invoke_on_movement, args=(self, instant_movement, objects_to_check, rects_to_check, site_rect))

            if not self.is_stuck:
                self._handle_x_movement(instant_movement, objects_to_check, rects_to_check)
                self._handle_y_movement(instant_movement, objects_to_check, rects_to_check)

            frame_movement -= unit_movement
            movement_length -= self.max_move_size

        if blit_site:
            blit_rect: FRect = FRect(*self.game.camera.position_world_to_display(site_position), *move_site)
            pygame.draw.rect(self.game.window.display, (255, 255, 0), blit_rect)
            
    def _handle_stucking(self, center: Vector2, objects_to_check: list[object],
                         rects_to_check: list[FRect]) -> Detected:
        stuck_causes: list[object] = []

        for obj, rect in zip(objects_to_check, rects_to_check):
            if rect.collidepoint(center):
                stuck_causes.append(obj)

        if stuck_causes:
            self.game.utilities.call_functions(
                self.invoke_on_stuck, args=(self, stuck_causes))

        return len(stuck_causes) > 0

    def _handle_x_movement(self, instant_movement: Vector2, objects_to_check: list[object],
                           rects_to_check: list[FRect]) -> None:
        self.position.x += instant_movement.x
        entity_rect: FRect = self.world_rect

        collide_right: list[object] = []
        collide_left: list[object] = []

        for obj, rect in zip(objects_to_check, rects_to_check):
            if entity_rect.colliderect(rect):
                if instant_movement.x > 0:
                    collide_right.append(obj)

                elif instant_movement.x < 0:
                    collide_left.append(obj)

        if collide_right:
            self.game.utilities.call_functions(
                self.invoke_on_collide_right, args=(self, collide_right))

        if collide_left:
            self.game.utilities.call_functions(
                self.invoke_on_collide_left, args=(self, collide_left))

    def _handle_y_movement(self, instant_movement: Vector2, objects_to_check: list[object],
                           rects_to_check: list[FRect]) -> None:
        self.position.y += instant_movement.y
        entity_rect: FRect = self.world_rect

        collide_bottom: list[object] = []
        collide_top: list[object] = []

        for obj, rect in zip(objects_to_check, rects_to_check):
            if entity_rect.colliderect(rect):
                if instant_movement.y > 0:
                    collide_bottom.append(obj)

                elif instant_movement.y < 0:
                    collide_top.append(obj)

        if collide_bottom:
            self.game.utilities.call_functions(
                self.invoke_on_collide_bottom, args=(self, collide_bottom))
        if collide_top:
            self.game.utilities.call_functions(
                self.invoke_on_collide_top, args=(self, collide_top))

    def basic_stuck(self, _, __) -> None:
        self.velocity = Vector2()

    def basic_collide_right(self, _, collide_right: list[object]) -> None:
        entity_rect = self.world_rect

        for obj in collide_right:
            entity_rect.right = obj.rect.left

        self.velocity.x = 0
        self.position.x = entity_rect.x

    def basic_collide_left(self, _, collide_left: list[object]) -> None:
        entity_rect = self.world_rect

        for obj in collide_left:
            entity_rect.left = obj.rect.right

        self.velocity.x = 0
        self.position.x = entity_rect.x

    def basic_collide_bottom(self, _, collide_bottom: list[object]) -> None:
        entity_rect = self.world_rect

        for obj in collide_bottom:
            entity_rect.bottom = obj.rect.top

        self.velocity.y = 0
        self.position.y = entity_rect.y

    def basic_collide_top(self, _, collide_top: list[object]) -> None:
        entity_rect = self.world_rect

        for obj in collide_top:
            entity_rect.top = obj.rect.bottom

        self.velocity.y = 0
        self.position.y = entity_rect.y
