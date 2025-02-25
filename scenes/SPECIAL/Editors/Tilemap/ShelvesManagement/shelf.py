from pygame import Surface, Vector2

from scenes.SPECIAL.Editors.Tilemap.ShelvesManagement.editor_tile import EditorTile
from scripts.AssetClasses.Tilemap.Tiles.tile import Tile
from scripts.AssetClasses.UI.Groups.ui_group import UI_Group
from scripts.AssetClasses.UI.button import Button
from scripts.AssetClasses.UI.scroll_zone import ScrollZone
from scripts.GameTypes import Position, UISheetPosition, HitboxType, UISheetVector


class Shelf:
    shelf_width = 200
    item_width = 50

    def __init__(self, shelves_manager: 'ShelvesManager', shelf_data: dict):
        self.game: 'Game' = shelves_manager.game
        self.sheet: 'UI_Sheet' = shelves_manager.sheet
        self.manager: 'ShelvesManager' = shelves_manager

        self.id = shelf_data["id"]
        self.editor_tiles: list[EditorTile] = []
        self._selected_tile_index: int = 0
        self._tiles_group: UI_Group = UI_Group(self.sheet, f"shelf tiles: {self.id}")
        self.shelf_group: UI_Group = UI_Group(self.sheet, f"shelf: {self.id}")
        self._scroll_zone: ScrollZone = None

        self.sheet.add_group(self.shelf_group)
        self._load_editor_tiles(shelf_data)
        self._create_ui_shelf()
        self._add_ui_elements_to_sheet()

    def _load_editor_tiles(self, shelf_data: dict) -> None:
        for editor_tile_data in shelf_data["editor_tiles"]:
            preview_data = editor_tile_data["preview"]
            tile_data = editor_tile_data["tile"]

            new_editor_tile: EditorTile = EditorTile(self, tile_data, preview_data)
            self.editor_tiles.append(new_editor_tile)

    def _create_ui_shelf(self) -> None:
        scroll_strip: Surface = self.game.assets.images["tilemap_editor/scroll_strip"]
        row_count: int = self.shelf_width // self.item_width

        position: UISheetPosition = Vector2(self.game.window.display_size[0] - self.shelf_width, 0)
        up_bound: float = -max(0, (len(self.editor_tiles) // row_count)-1) * self.item_width
        self.scroll_zone = ScrollZone(self.game, self.sheet, f"sz: {self.id}", position, 10, False,
                                      HitboxType.RECTANGLE, 0, True,
                                      scroll_strip, scroll_strip, scroll_strip, 40,
                                      (Vector2(0, 0), Vector2(up_bound, 0)), True, True)

        self.shelf_group.elements.add(self.scroll_zone)
        self.scroll_zone.group = self._tiles_group

        for i, tile in enumerate(self.editor_tiles):
            offset: UISheetVector = Vector2(
                (i % row_count) * self.item_width,
                (i // row_count) * self.item_width)

            ui_img: Surface = tile.ui_image

            tile_button: Button = Button(
                self.game, self.sheet, f"shelf {self.id};{i}", position + offset, 15, False,
                0, True, HitboxType.RECTANGLE, ui_img, ui_img, ui_img, ui_img)

            tile_button.invoke_on_press.add((0, f"{self.id};{i}", self._select_tile_callback))

            self.shelf_group.elements.add(tile_button)
            self._tiles_group.elements.add(tile_button)

    def _select_tile_callback(self, button: Button) -> None:
        self._selected_tile_index = int(button.name.split(";")[1])

    def _add_ui_elements_to_sheet(self) -> None:
        for element in self.shelf_group.elements:
            self.sheet.add_element(element)

        self.sheet.add_group(self.shelf_group)
        self.sheet.add_group(self._tiles_group)

    @property
    def valid_selection(self) -> bool:
        return len(self.editor_tiles) > 0

    @property
    def selected_editor_tile(self) -> EditorTile | None:
        if not self.valid_selection:
            return None

        return self.editor_tiles[self._selected_tile_index]

    def get_preview_image(self, grid: 'Grid', offgrid: bool) -> Surface | None:
        if not self.valid_selection:
            return None

        return self.editor_tiles[self._selected_tile_index].get_preview_image(grid, offgrid)

    def get_tile_object(self, grid: 'Grid', offgrid: bool, position: Position) -> Tile | None:
        if not self.valid_selection:
            return None

        return self.editor_tiles[self._selected_tile_index].get_tile_object(grid, offgrid, position)

    def increment_selection(self, increment: int=1) -> None:
        self._selected_tile_index += increment
        self._selected_tile_index %= len(self.editor_tiles)

    def decrement_selection(self, decrement: int = 1) -> None:
        self._selected_tile_index -= decrement
        self._selected_tile_index %= len(self.editor_tiles)
