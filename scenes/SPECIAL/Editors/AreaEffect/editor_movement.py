from scenes.SPECIAL.Editors.AreaEffect.effect_editor import EffectEditor
from scripts.AssetClasses.Tilemap.tilemap import Tilemap
from scripts.AssetClasses.scene import Scene


class EditorMovement:
    def __init__(self, editor: EffectEditor):
        self.game: 'Game' = editor.game
        self.editor: EffectEditor = editor
        self.tilemap: Tilemap = editor.tilemap
        self.scene: Scene = editor.scene

        self.dragging: bool = False

        self.game.inputs.on_mousewheel_press.add(
            (0, "TilemapEditor drag on", self.dragging_on, self.scene))
        self.game.inputs.on_mousewheel_let.add(
            (0, "TilemapEditor drag off", self.dragging_off, self.scene))

    def update(self) -> None:
        if self.dragging:
            self.game.camera.position += -self.game.mouse.delta

    def dragging_on(self) -> None:
        self.dragging = True

    def dragging_off(self) -> None:
        self.dragging = False
