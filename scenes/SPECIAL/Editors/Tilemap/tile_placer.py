from pygame import Vector2

from scenes.SPECIAL.Editors.Tilemap.ShelvesManagement.shelf import Shelf
from scenes.SPECIAL.Editors.Tilemap.editor import TilemapEditor
from scripts.AssetClasses.Tilemap.grid import Grid
from scripts.AssetClasses.Tilemap.Tiles.tile import Tile
from scripts.AssetClasses.Tilemap.tilemap import Tilemap
import pygame

from scripts.AssetClasses.UI.ui_sheet import UI_Sheet
from scripts.AssetClasses.scene import Scene
from scripts.GameTypes import GridPosition, TilePosition, DisplayPosition, Percentage, PixelPos_2_Position


class TilePlacer:
    def __init__(self, editor: TilemapEditor):
        self.game: 'Game' = editor.game
        self.tilemap: Tilemap = editor.tilemap
        self.sheet: UI_Sheet = editor.sheet
        self.scene: Scene = editor.scene
        self.editor: TilemapEditor = editor

        self.placing_on_grid: bool = True
        self.focus_offgrid_background: bool = True
        self.placing: bool = False
        self.deleting: bool = False
        self.snapon: bool = False

        self.hint_alpha: Percentage = 0.4

        self._add_callbacks()

    def _add_callbacks(self) -> None:
        self.game.inputs.on_lshift_press.add(
            (-20, "Tileplacer toggle placing on grid", self.toggle_placing_on_grid, self.scene))
        self.sheet.elements["Placing on grid"].invoke_on_toggle.add(
            (0, "Tileplacer placing on grid callback", self.placing_on_grid_callback, self.scene))

        self.game.inputs.on_tab_press.add(
            (-20, "Tileplacer toggle focusing offgrid background",
             self.toggle_focusing_offgrid_background, self.scene))
        self.sheet.elements["Focus offgrid background"].invoke_on_toggle.add(
            (0, "Tileplacer focus offgrid background callback",
             self.focus_offgrid_background_callback, self.scene))

        self.game.inputs.on_ctrl_press.add(
            (-20, "Tileplacer toggle snapon", self.toggle_snapon, self.scene))
        self.sheet.elements["SNAPON"].invoke_on_toggle.add(
            (0, "Tileplacer snapon callback", self.snapon_callback, self.scene))

        self.game.inputs.on_mouse_left_press.add(
            (1, "TilePlacer callback", self.on_left_click_press, self.scene))
        self.game.inputs.on_mouse_left_let.add(
            (1, "TilePlacer callback", self.on_left_click_let, self.scene))

        self.game.inputs.on_mouse_right_press.add(
            (1, "TilePlacer callback", self.on_right_click_press, self.scene))
        self.game.inputs.on_mouse_right_let.add(
            (1, "TilePlacer callback", self.on_right_click_let, self.scene))

        self.game.inputs.on_mouse_scroll_up.add(
            (1, "Tile up", self.tile_up, self.scene))
        self.game.inputs.on_mouse_scroll_down.add(
            (1, "Tile down", self.tile_down, self.scene))

    def tile_up(self) -> None:
        if not self.can_place:
            return

        shelf: Shelf = self.editor.shelves_manager.selected_shelf
        shelf.decrement_selection()

    def tile_down(self) -> None:
        if not self.can_place:
            return

        shelf: Shelf = self.editor.shelves_manager.selected_shelf
        shelf.increment_selection()

    def toggle_placing_on_grid(self) -> None:
        self.placing_on_grid = not self.placing_on_grid
        self.sheet.elements["Placing on grid"].is_on = self.placing_on_grid

    def toggle_focusing_offgrid_background(self) -> None:
        self.focus_offgrid_background = not self.focus_offgrid_background
        self.sheet.elements["Focus offgrid background"].is_on = self.focus_offgrid_background

    def toggle_snapon(self) -> None:
        self.snapon = not self.snapon
        self.sheet.elements["SNAPON"].is_on = self.snapon

    def placing_on_grid_callback(self, toggle: 'Toggle') -> None:
        self.placing_on_grid = toggle.is_on

    def focus_offgrid_background_callback(self, toggle: 'Toggle') -> None:
        self.focus_offgrid_background = toggle.is_on

    def snapon_callback(self, toggle: 'Toggle') -> None:
        self.snapon = toggle.is_on

    @property
    def can_place(self) -> bool:
        if self.editor.selected_grid is None:
            return False

        if self.sheet.intersecting_mouse:
            return False

        if not self.editor.shelves_manager.valid_selection:
            return False

        return True

    @property
    def performing(self) -> bool:
        return self.placing or self.deleting

    @property
    def preview_image(self) -> pygame.Surface:
        return self.editor.shelves_manager.get_preview_image()

    @property
    def hint_image(self) -> pygame.Surface:
        hint_image: pygame.Surface = self.preview_image.copy()
        hint_image.set_alpha(round(255 * self.hint_alpha))

        return hint_image

    @property
    def mouse_tile_pos(self) -> TilePosition:
        grid: Grid = self.editor.get_selected_grid()
        return grid.position_display_to_tile(self.game.mouse.position)

    @property
    def mouse_grid_pos(self) -> GridPosition:
        grid: Grid = self.editor.get_selected_grid()
        return grid.position_world_to_grid(self.game.mouse.world_position)

    @property
    def mouse_grid_snapon_pos(self) -> GridPosition:
        position: TilePosition = self.mouse_tile_pos
        grid: Grid = self.editor.get_selected_grid()
        return grid.position_tile_to_grid(position)

    def update(self) -> None:
        self._handle_tile_on_grid()
        self._blit_hint()

    def _handle_tile_on_grid(self) -> None:
        if not self.performing or not self.can_place:
            return

        if self.placing and self.placing_on_grid:
            self._place_tile_on_grid()
        elif self.deleting and self.placing_on_grid:
            self._delete_tile_on_grid()
        elif self.deleting and not self.placing_on_grid:
            self._delete_tile_off_grid()

    def on_left_click_press(self) -> None:
        if not self.editor.scene.active:
            return

        self.placing = True

        if self.can_place and not self.placing_on_grid:
            self._place_tile_off_grid()

    def on_left_click_let(self) -> None:
        if not self.editor.scene.active:
            return

        self.placing = False

    def on_right_click_press(self) -> None:
        if not self.editor.scene.active:
            return

        self.deleting = True

    def on_right_click_let(self) -> None:
        if not self.editor.scene.active:
            return

        self.deleting = False

    def _place_tile_on_grid(self) -> None:
        grid: Grid = self.editor.get_selected_grid()
        position: TilePosition = self.mouse_tile_pos
        tile: Tile = self.editor.shelves_manager.get_tile_object(Vector2(*position))

        if tile is None:
            raise Exception("tile is none in _place_tile_on_grid, should not happen")

        grid.tiles[position] = tile

    def _delete_tile_on_grid(self) -> None:
        grid: Grid = self.editor.get_selected_grid()
        position: TilePosition = self.mouse_tile_pos

        if position not in grid.tiles:
            return

        del grid.tiles[position]

    def _place_tile_off_grid(self) -> None:
        grid: Grid = self.editor.get_selected_grid()
        tile: Tile = self.editor.shelves_manager.get_tile_object(Vector2())

        if tile is None:
            raise Exception("tile is None in _place_tile_off_grid, should not happen")

        if self.snapon:
            position: GridPosition = self.mouse_grid_snapon_pos
        else:
            position: GridPosition = self.mouse_grid_pos
            position -= 0.5 * PixelPos_2_Position(tile.offgrid_size_function(tile))

        tile.position = (position.x, position.y)

        if self.focus_offgrid_background:
            if tile in grid.offgrid_background:
                return

            grid.offgrid_background.add(tile)
        else:
            if tile in grid.offgrid_foreground:
                return

            grid.offgrid_foreground.add(tile)

    def _delete_tile_off_grid(self) -> None:
        grid: Grid = self.editor.get_selected_grid()
        position: GridPosition = self.mouse_grid_pos

        offgrid_tiles: list[Tile] = []
        tiles_to_remove: list[Tile] = []
        if self.focus_offgrid_background:
            offgrid_tiles = list(grid.offgrid_background)
        else:
            offgrid_tiles = list(grid.offgrid_foreground)

        for tile in offgrid_tiles:
            if not tile.grid_rect.collidepoint(*position):
                continue

            tiles_to_remove.append(tile)

        for tile in tiles_to_remove:
            if self.focus_offgrid_background:
                grid.offgrid_background.remove(tile)
            else:
                grid.offgrid_foreground.remove(tile)

    def _blit_hint(self) -> None:
        if not self.can_place:
            return

        hint_image: pygame.Surface = self.hint_image

        if self.placing_on_grid:
            grid: Grid = self.editor.get_selected_grid()
            tile_pos: TilePosition = self.mouse_tile_pos
            blit_pos: DisplayPosition = grid.position_tile_to_display(tile_pos)

        else:
            if self.snapon:
                grid: Grid = self.editor.get_selected_grid()
                blit_pos: DisplayPosition = grid.position_grid_to_display(self.mouse_grid_snapon_pos)
            else:
                blit_pos: DisplayPosition = self.game.mouse.position.copy()
                blit_pos -= 0.5 * PixelPos_2_Position(hint_image.get_size())

        self.game.window.display.blit(hint_image, blit_pos)
