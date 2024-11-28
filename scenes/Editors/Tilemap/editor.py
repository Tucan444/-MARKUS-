import pygame
from pygame import Vector2

from scenes.scene_behaviour import SceneBehaviour
from scripts.AssetClasses.Tilemap.grid import Grid
from scripts.AssetClasses.Tilemap.tilemap import Tilemap
from scripts.AssetClasses.UI.ui_sheet import UI_Sheet


# todo add tile shelf, from /tiles folder in images/animations - [game specific]
# todo add tile folders - [game specific]
# todo add carousel of tiles, normal / animated
class TilemapEditor(SceneBehaviour):
    def __init__(self, game, scene, active, order):
        super().__init__(game, scene, active, order)

        self.tilemap_name: str = "boilmap"
        self.ui_sheet_name: str = "tilemap editor main"

        self.tilemap: Tilemap | None = None
        self.sheet: UI_Sheet | None = None

        self.selected_grid: int | None = None
        self.editor_grid_ui: "TilemapEditorGridUI" | None = None
        self.tile_placer: 'TilePlacer' | None = None
        self.editor_movement: 'EditorMovement' | None = None

        self.enforce_different_layer: bool = True
        self.save_compact: bool = False

        self.tile_images: dict[str, pygame.Surface] = {
           name : image for name, image in self.game.assets.images.items() if name.startswith("tiles/")
        }
        self.tile_names: list[str] = [name for name in self.tile_images.keys()]

        print(self.tile_images)

    def init(self):
        self.tilemap = self.game.assets.tilemaps[self.tilemap_name]
        self.check_for_layer_indifference()

        self.sheet = self.game.assets.ui_sheets[self.ui_sheet_name]
        self.sheet.active = True

        self.sheet.groups["GridGroup"].move_elements(Vector2(-250, 0))
        self.editor_grid_ui = self.scene.classes["TilemapEditorGridUI"](self)
        self.tile_placer = self.scene.classes["TilePlacer"](self)
        self.editor_movement = self.scene.classes["EditorMovement"](self)

        self.sheet.elements["TILEMAP TITLE"].text = self.tilemap_name
        self.sheet.elements["ADD GRID"].invoke_on_press.add(
            (5, "Adding grid", self.add_grid)
        )
        self.sheet.elements["REMOVE GRID"].invoke_on_press.add(
            (5, "Removing grid", self.remove_selected_grid)
        )
        self.sheet.elements["SAVE COMPACT"].invoke_on_toggle.add(
            (5, "Change compact saving of tilemap", self.toggle_compact_saving_callback)
        )

    def update(self):
        self.tilemap.blit_faded()
        self.tilemap.update_animations()
        self.sheet.blit()
        self.tile_placer.update()
        self.editor_movement.update()

    def end(self):
        self.sheet.active = False
        self.tilemap.save(compact=self.save_compact)

    def add_grid(self, call_object) -> None:
        index: int = 1 + len(self.tilemap.grids_ordered)
        while (new_name := f"{index}") in self.tilemap.grids:
            index += 1

        new_grid: Grid = Grid(self.tilemap, new_name,
                              self.tilemap.standard_tile_size,
                              0 if self.selected_grid is None else self.tilemap.grids_ordered[self.selected_grid].layer + 1,
                              True, 0, False, False, False, 1, 0)

        self.tilemap.add_grid(new_grid)
        self.check_for_layer_indifference()
        self.editor_grid_ui.refresh()
        self.selected_grid = None

    def check_for_layer_indifference(self) -> None:
        if not self.enforce_different_layer:
            return

        upper: int = 0
        for i in range(0, len(self.tilemap.grids_ordered) - 1):
            j = i + 1

            first: Grid = self.tilemap.grids_ordered[i]
            second: Grid = self.tilemap.grids_ordered[j]

            second.layer += upper
            if first.layer == second.layer:
                upper += 1
                second.layer += 1

    def remove_selected_grid(self, call_object) -> None:
        if self.selected_grid is None:
            return

        self.tilemap.remove_grid(self.tilemap.grids_ordered[self.selected_grid])
        self.editor_grid_ui.refresh()
        self.selected_grid = None

    def get_selected_grid(self) -> Grid | None:
        if self.selected_grid is None:
            return None

        return self.tilemap.grids_ordered[self.selected_grid]

    def toggle_compact_saving_callback(self, toggle: 'Toggle') -> None:
        self.save_compact = toggle.is_on
