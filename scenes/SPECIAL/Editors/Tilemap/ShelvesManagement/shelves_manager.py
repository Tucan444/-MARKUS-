import os
import json

from pygame import Surface, Vector2

from scenes.SPECIAL.Editors.Tilemap.ShelvesManagement.shelf import Shelf
from scenes.SPECIAL.Editors.Tilemap.editor import TilemapEditor
from scripts.AssetClasses.Tilemap.Tiles.tile import Tile
from scripts.AssetClasses.UI.button import Button
from scripts.DataStructures.sorted_array import SortedArray
from scripts.GameTypes import Position, UISheetPosition, HitboxType


class ShelvesManager:
    def __init__(self, editor: TilemapEditor):
        self.game: 'Game' = editor.game
        self.scene: 'Scene' = editor.scene
        self.editor: TilemapEditor = editor
        self.tilemap: 'Tilemap' = self.editor.tilemap
        self.sheet: 'UI_Sheet' = self.editor.sheet

        self.shelves: SortedArray = SortedArray(Shelf, key=lambda x:x.id)
        # shelf 0(images), shelf 1(animations) are special
        self._generate_ui_buttons()
        self._generate_special_shelves()
        self._load_shelves()
        self._selected_shelf_index: int = 0
        self._last_custom_shelf_index: int = 2

        self.selected_shelf.shelf_group.set_active(True)

    def _generate_ui_buttons(self) -> None:
        position: UISheetPosition = Vector2(self.game.window.display_size[0] - Shelf.shelf_width - 100, 0)

        custom_button: Button = Button(
            self.game, self.sheet, "custom shelf select", position, 10, True, 0, True,
            HitboxType.RECTANGLE, self.game.assets.images["tilemap_editor/toolbar/custom_shelf"],
            self.game.assets.images["tilemap_editor/toolbar/custom_shelf_hover"],
            self.game.assets.images["tilemap_editor/toolbar/custom_shelf_pressed"],
            self.game.assets.images["tilemap_editor/toolbar/custom_shelf_pressed"]
        )

        video_button: Button = Button(
            self.game, self.sheet, "video shelf select", position + Vector2(50, 0),
            10, True, 0, True,
            HitboxType.RECTANGLE, self.game.assets.images["tilemap_editor/toolbar/video_shelf"],
            self.game.assets.images["tilemap_editor/toolbar/video_shelf_hover"],
            self.game.assets.images["tilemap_editor/toolbar/video_shelf_pressed"],
            self.game.assets.images["tilemap_editor/toolbar/video_shelf_pressed"]
        )

        image_button: Button = Button(
            self.game, self.sheet, "image shelf select", position + Vector2(50, 50),
            10, True, 0, True,
            HitboxType.RECTANGLE, self.game.assets.images["tilemap_editor/toolbar/image_shelf"],
            self.game.assets.images["tilemap_editor/toolbar/image_shelf_hover"],
            self.game.assets.images["tilemap_editor/toolbar/image_shelf_pressed"],
            self.game.assets.images["tilemap_editor/toolbar/image_shelf_pressed"]
        )

        shelf_up_button: Button = Button(
            self.game, self.sheet, "shelf up button", position + Vector2(0, 50),
            10, True, 0, True,
            HitboxType.RECTANGLE, self.game.assets.images["tilemap_editor/toolbar/shelf_up"],
            self.game.assets.images["tilemap_editor/toolbar/shelf_up_hover"],
            self.game.assets.images["tilemap_editor/toolbar/shelf_up_pressed"],
            self.game.assets.images["tilemap_editor/toolbar/shelf_up_pressed"]
        )

        shelf_down_button: Button = Button(
            self.game, self.sheet, "shelf down button", position + Vector2(0, 75),
            10, True, 0, True,
            HitboxType.RECTANGLE, self.game.assets.images["tilemap_editor/toolbar/shelf_down"],
            self.game.assets.images["tilemap_editor/toolbar/shelf_down_hover"],
            self.game.assets.images["tilemap_editor/toolbar/shelf_down_pressed"],
            self.game.assets.images["tilemap_editor/toolbar/shelf_down_pressed"]
        )

        self.sheet.add_element(custom_button)
        self.sheet.add_element(video_button)
        self.sheet.add_element(image_button)
        self.sheet.add_element(shelf_up_button)
        self.sheet.add_element(shelf_down_button)

        custom_button.invoke_on_press.add((0, "custom_shelf_callback", self._custom_shelf_callback))
        video_button.invoke_on_press.add((0, "video_shelf_callback", self._video_shelf_callback))
        image_button.invoke_on_press.add((0, "image_shelf_callback", self._image_shelf_callback))
        shelf_up_button.invoke_on_press.add((0, "shelf_up_callback", self._shelf_up_callback))
        shelf_down_button.invoke_on_press.add((0, "shelf_down_callback", self._shelf_down_callback))

    def _generate_special_shelves(self) -> None:
        self._generate_image_shelf()
        self._generate_animation_shelf()

    def _generate_image_shelf(self) -> None:
        priorities: list[str] = [
            name for name, _ in self.game.assets.images.items() if name.startswith("tiles/")]

        other: list[str] = [
            name for name, _ in self.game.assets.images.items() if not name.startswith("tiles/")]

        image_names: list[str] = priorities + other
        del priorities, other # manual memory management UwU

        shelf_data: dict = {
            "id": -100_000_001,
            "editor_tiles": [
                {
                    "preview": {},
                    "tile": {
                        "image": name
                    }
                } for name in image_names
            ]
        }

        new_shelf: 'Shelf' = Shelf(self, shelf_data)
        self.shelves.add(new_shelf)

    def _generate_animation_shelf(self) -> None:
        priorities: list[str] = [
            name for name, _ in self.game.assets.animations.items() if name.startswith("tiles/")]

        other: list[str] = [
            name for name, _ in self.game.assets.animations.items() if not name.startswith("tiles/")]

        animation_names: list[str] = priorities + other
        del priorities, other  # manual memory management UwU

        shelf_data: dict = {
            "id": -100_000_000,
            "editor_tiles": [
                {
                    "preview": {},
                    "tile": {
                        "animation": name
                    }
                } for name in animation_names
            ]
        }

        new_shelf: 'Shelf' = Shelf(self, shelf_data)
        self.shelves.add(new_shelf)

    def _load_shelves(self) -> None:
        # todo make recursive
        shelves_path: str = f"{self.scene.path}/Shelves"

        for filepath in os.listdir(shelves_path):
            if not filepath.endswith(".json"):
                continue

            with open(f"{shelves_path}/{filepath}", 'r') as f:
                shelf_data: dict = json.load(f)
                new_shelf: 'Shelf' = Shelf(self, shelf_data)
                self.shelves.add(new_shelf)

    def _custom_shelf_callback(self, _: Button) -> None:
        if self._last_custom_shelf_index >= len(self.shelves):
            return

        self.increment_selection(self._last_custom_shelf_index - self._selected_shelf_index)

    def _video_shelf_callback(self, _: Button) -> None:
        if self._selected_shelf_index > 1:
            self._last_custom_shelf_index = self._selected_shelf_index

        self.increment_selection(1 - self._selected_shelf_index)

    def _image_shelf_callback(self, _: Button) -> None:
        if self._selected_shelf_index > 1:
            self._last_custom_shelf_index = self._selected_shelf_index


        self.decrement_selection(self._selected_shelf_index)

    def _shelf_up_callback(self, _: Button) -> None:
        self.increment_selection()

        if self._selected_shelf_index > 1:
            self._last_custom_shelf_index = self._selected_shelf_index

    def _shelf_down_callback(self, _: Button) -> None:
        self.decrement_selection()

        if self._selected_shelf_index > 1:
            self._last_custom_shelf_index = self._selected_shelf_index

    @property
    def valid_selection(self) -> bool:
        return self.selected_shelf.valid_selection

    @property
    def selected_shelf(self) -> Shelf:
        return self.shelves[self._selected_shelf_index]

    def get_preview_image(self) -> Surface | None:
        offgrid: bool = self.editor.offgrid
        grid: 'Grid' | None = self.editor.get_selected_grid()

        if grid is None:
            return None

        return self.shelves[self._selected_shelf_index].get_preview_image(grid, offgrid)

    def get_tile_object(self, position: Position) -> Tile | None:
        offgrid: bool = self.editor.offgrid
        grid: 'Grid' | None = self.editor.get_selected_grid()

        if grid is None:
            return None

        return self.shelves[self._selected_shelf_index].get_tile_object(grid, offgrid, position)

    def increment_selection(self, increment: int=1) -> None:
        self.selected_shelf.shelf_group.set_active(False)

        self._selected_shelf_index += increment
        self._selected_shelf_index %= len(self.shelves)

        self.selected_shelf.shelf_group.set_active(True)

    def decrement_selection(self, decrement: int = 1) -> None:
        self.selected_shelf.shelf_group.set_active(False)

        self._selected_shelf_index -= decrement
        self._selected_shelf_index %= len(self.shelves)

        self.selected_shelf.shelf_group.set_active(True)
