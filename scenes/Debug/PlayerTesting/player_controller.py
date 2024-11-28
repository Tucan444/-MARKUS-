from pygame import Vector2

from scripts.GameTypes import WorldVector
from scripts.Utilities.physics_entity import PhysicsEntity


class PlayerController:
    def __init__(self, world: 'World'):
        self.world: 'World' = world
        self.game: 'Game' = world.game
        self.scene: 'Scene' = self.world.scene
        self.player: PhysicsEntity = self.world.player

        self.pressed: dict[str, bool] = {
            "right": False,
            "left": False
        }

        self.game.inputs.on_up_press.add((0, "jump", self.on_top_press, self.scene))
        self.game.inputs.on_right_press.add((0, "go right", self.on_press_right, self.scene))
        self.game.inputs.on_right_let.add((0, "go right not", self.on_let_right, self.scene))
        self.game.inputs.on_left_press.add((0, "go left", self.on_left_press, self.scene))
        self.game.inputs.on_left_let.add((0, "go left not", self.on_left_let, self.scene))

    @property
    def movement(self) -> WorldVector:
        return Vector2(
            (250 if self.pressed["right"] else 0) + (-250 if self.pressed["left"] else 0), 0
        )

    def on_top_press(self) -> None:
        self.player.velocity.y = -500

    def on_left_press(self) -> None:
        self.pressed["left"] = True

    def on_left_let(self) -> None:
        self.pressed["left"] = False

    def on_press_right(self) -> None:
        self.pressed["right"] = True

    def on_let_right(self) -> None:
        self.pressed["right"] = False
