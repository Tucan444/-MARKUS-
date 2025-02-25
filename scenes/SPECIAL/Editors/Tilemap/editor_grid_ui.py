import pygame.math

from scenes.SPECIAL.Editors.Tilemap.editor import TilemapEditor
from scripts.AssetClasses.Tilemap.grid import Grid
from scripts.AssetClasses.UI.Groups.ui_group import UI_Group
from scripts.GameTypes import Index


class GridUI:
    def __init__(self, sheet: 'UI_Sheet', grid: Grid):
        self.game: 'Game' = sheet.game
        self.sheet: 'UI_Sheet' = sheet
        self.grid: Grid = grid

        self.elements: list['UI_Element'] = []
        self.ui_group: UI_Group | None = None
        self.select_toggle: 'Toggle' | None = None

        self._init_from_template()
        self._create_move_group()

    def _init_from_template(self) -> None:
        for elem in self.sheet.groups["GridGroup"].elements:
            self._load_elem(elem)

    def _load_elem(self, element: 'UI_Element') -> None:
        elm = element.clone

        if elm.name == "GridSelect":
            self.select_toggle = elm
        elif elm.name == "GridTitle":
            elm.text = self.grid.name
        elif elm.name == "GridSliderTileSize":
            pass
        elif elm.name == "GridSliderDepth":
            elm.value = self.grid.depth
        elif elm.name == "GridSliderAlpha":
            elm.value = self.grid.alpha
        elif elm.name == "GridActive":
            elm.is_on = self.grid.active
        elif elm.name == "GridUseDepth":
            elm.is_on = self.grid.use_depth
        elif elm.name == "GridPhysical":
            elm.is_on = self.grid.physical
        elif elm.name == "GridInvisible":
            elm.is_on = self.grid.invisible

        elm.name = f"{elm.name};{self.grid.name}"
        self.elements.append(elm)
        self.sheet.add_element(elm)

    def _create_move_group(self) -> None:
        self.ui_group = UI_Group(self.sheet, f"GridGroup, elements {len(self.elements)}, grid {self.grid.name}")

        for element in self.elements:
            self.ui_group.elements.add(element)

    def delete(self) -> None:
        self.ui_group.detach()
        self.ui_group.clear()


class TilemapEditorGridUI:
    def __init__(self, editor: TilemapEditor):
        self.game: 'Game' = editor.game
        self.editor: TilemapEditor = editor
        self.tilemap: 'Tilemap' = self.editor.tilemap
        self.sheet: 'UI_Sheet' = self.editor.sheet

        self.ui_grids: list[GridUI] = []
        self._create_grids()

    def refresh(self) -> None:
        self._clear_grids()

        self._create_grids()

    def _clear_grids(self) -> None:
        self.sheet.groups["GridSelect"].clear()

        for grid in self.ui_grids:
            grid.delete()

        self.ui_grids = []

        scroll_zone: 'ScrollZone' = self.sheet.elements["DEEP"]
        scroll_zone.group.clear()
        scroll_zone.scroll_position = pygame.math.Vector2(0, 0)
        scroll_zone.y_scroll_bound = pygame.math.Vector2(0, 0)

    def _create_grids(self) -> None:
        for i, grid in enumerate(reversed(self.tilemap.grids_ordered)):
            self.create_grid(i, grid)

        self.sheet.elements["DEEP"].y_scroll_bound = pygame.math.Vector2(
            -100 * max(0, len(self.ui_grids) - 1),
            0.0
        )

        self.ui_grids.reverse()

    def create_grid(self, index: int, grid: 'Grid') -> None:
        grid_ui: GridUI = GridUI(self.sheet, grid)
        grid_ui.ui_group.move_elements(pygame.math.Vector2(0, 100 * (index + 1)))
        self.sheet.elements["DEEP"].add_elements(*grid_ui.elements)

        self.ui_grids.append(grid_ui)
        self.sheet.groups["GridSelect"].add_toggle(grid_ui.select_toggle)

        self.add_callbacks_to_grid(grid_ui)

    def add_callbacks_to_grid(self, grid_ui: GridUI) -> None:
        for elm in grid_ui.elements:
            name: str = elm.name.split(";")[0]

            if name == "GridSelect":
                elm.invoke_on_toggle.add(
                    (-10, f"grid selected {grid_ui.grid.name}", self.select_grid_callback)
                )
            elif name == "GridTitle":
                pass
            elif name == "GridSliderTileSize":
                pass
            elif name == "GridSliderDepth":
                elm.invoke_on_value_change.add(
                    (-10, f"grid depth change {grid_ui.grid.name}", self.depth_grid_callback)
                )
            elif name == "GridSliderAlpha":
                elm.invoke_on_value_change.add(
                    (-10, f"grid alpha change {grid_ui.grid.name}", self.alpha_grid_callback)
                )
            elif name == "GridActive":
                elm.invoke_on_toggle.add(
                    (-10, f"grid active {grid_ui.grid.name}", self.active_grid_callback)
                )
            elif name == "GridUseDepth":
                elm.invoke_on_toggle.add(
                    (-10, f"grid use depth {grid_ui.grid.name}", self.use_depth_grid_callback)
                )
            elif name == "GridPhysical":
                elm.invoke_on_toggle.add(
                    (-10, f"grid physical {grid_ui.grid.name}", self.physical_grid_callback)
                )
            elif name == "GridInvisible":
                elm.invoke_on_toggle.add(
                    (-10, f"grid invisible {grid_ui.grid.name}", self.invisible_grid_callback)
                )
            elif name == "GridLayerUp":
                elm.invoke_on_press.add(
                    (-10, f"grid layer up {grid_ui.grid.name}", self.layer_up_callback)
                )
            elif name == "GridLayerDown":
                elm.invoke_on_press.add(
                    (-10, f"grid layer down {grid_ui.grid.name}", self.layer_down_callback)
                )

    def get_grid_by_name(self, name: str) -> tuple[Grid, Index] | None:
        for i, grid in enumerate(self.tilemap.grids_ordered):
            if grid.name == name:
                return grid, i

        return None

    def select_grid_callback(self, toggle: 'Toggle') -> None:
        grid, index = self.get_grid_by_name(toggle.name.split(";")[1])

        self.editor.selected_grid = index

    def layer_up_callback(self, button: 'Button') -> None:
        grid, index = self.get_grid_by_name(button.name.split(";")[1])

        if index == len(self.tilemap.grids_ordered) - 1:
            return

        grid.layer = self.tilemap.grids_ordered[index + 1].layer + 1
        self.tilemap.grids_ordered.sort(key=lambda x: x.layer)

        if self.editor.enforce_different_layer:
            for i in range(index + 2, len(self.tilemap.grids_ordered)):
                self.tilemap.grids_ordered[i].layer += 1

        self.refresh()

    def layer_down_callback(self, button: 'Button') -> None:
        grid, index = self.get_grid_by_name(button.name.split(";")[1])

        if index == 0:
            return

        grid.layer = self.tilemap.grids_ordered[index - 1].layer - 1
        self.tilemap.grids_ordered.sort(key=lambda x: x.layer)

        if self.editor.enforce_different_layer:
            for i in range(index - 2, -1, -1):
                self.tilemap.grids_ordered[i].layer -= 1

        self.refresh()

    def invisible_grid_callback(self, toggle: 'Toggle') -> None:
        grid, index = self.get_grid_by_name(toggle.name.split(";")[1])

        grid.invisible = toggle.is_on

    def physical_grid_callback(self, toggle: 'Toggle') -> None:
        grid, index = self.get_grid_by_name(toggle.name.split(";")[1])

        grid.physical = toggle.is_on

    def use_depth_grid_callback(self, toggle: 'Toggle') -> None:
        grid, index = self.get_grid_by_name(toggle.name.split(";")[1])

        grid.use_depth = toggle.is_on

    def active_grid_callback(self, toggle: 'Toggle') -> None:
        grid, index = self.get_grid_by_name(toggle.name.split(";")[1])

        grid.active = toggle.is_on

    def depth_grid_callback(self, slider: 'Slider') -> None:
        grid, index = self.get_grid_by_name(slider.name.split(";")[1])

        grid.depth = slider.value

    def alpha_grid_callback(self, slider: 'Slider') -> None:
        grid, index = self.get_grid_by_name(slider.name.split(";")[1])

        grid.alpha = slider.value
