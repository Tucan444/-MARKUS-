import json

from scripts.AssetClasses.UI.Groups.ui_group import UI_Group
from scripts.AssetClasses.UI.ui_element import UI_Element
from scripts.DataStructures.sorted_array import SortedArray
from scripts.GameTypes import DisplayPosition, UISheetPosition, SortableFunction


class UI_Sheet:
    def __init__(self, game: 'Game', name: str, filepath: str, position: DisplayPosition, in_world: bool, active: bool=False):
        self.game: 'Game' = game
        self.name: str = name
        self.filepath: str = filepath
        self.position: DisplayPosition = position
        self.in_world: bool = in_world
        self.active: bool = active

        self.elements: dict[str, UI_Element] = {}
        self.elements_ordered: SortedArray = SortedArray(UI_Element, key=self._element_comparator)

        self.groups: dict[str, UI_Group] = {}

        self._intersecting_mouse: bool = False
        self._last_frame_update: int = -1
        self._top_element: UI_Element | None = None

    def save(self, compact: bool=True) -> None:
        with open(self.filepath, "w") as f:
            if compact:
                json.dump(self.as_json, f, separators=(',', ':'), indent=None)
            else:
                json.dump(self.as_json, f, indent=4)

    def clear(self) -> None:
        for element in list(self.elements.values()):
            element.detach()

        self.elements = {}
        self.elements_ordered.clear()

        self.groups = {}

    def reload(self):
        self.clear()

        sheet: UI_Sheet = self.game.utilities.load_ui_sheet(
            self.filepath[1+len(self.game.utilities.DEFAULT_UI_SHEET_PATH):], self.game)

        self.name = sheet.name
        self.position = sheet.position
        self.in_world = sheet.in_world

        self.elements = sheet.elements
        self.elements_ordered = sheet.elements_ordered
        for element in self.elements_ordered:
            element.ui_sheet = self

        self.groups = sheet.groups
        for group in self.groups.values():
            group.ui_sheet = self

        self._intersecting_mouse = False
        self._last_frame_update = -1
        self._top_element = None

    @property
    def as_json(self) -> dict:
        json_form: dict = {
            "type": "ui sheet",
            "name": self.name,
            "position": list(self.position),
            "in world": self.in_world,
            "elements": [
                element.as_json for element in self.elements_ordered
            ],
            "groups": [
                group.as_json for group in self.groups.values()
            ]
        }

        return json_form

    @property
    def as_string(self) -> str:
        return (f"name: {self.name}, filepath: {self.filepath}, position: {self.position},"
                f"number of elements: {len(self.elements_ordered)}, "
                f"number of groups: {len(self.groups)}")

    def __repr__(self):
        return self.as_string

    def __str__(self):
        return self.as_string

    @property
    def clone(self) -> 'UI_Sheet':
        return self.game.utilities.load_ui_sheet_from_data(self.as_json, self.filepath, self.game)

    def _update_runtime_information(self) -> None:
        self._intersecting_mouse = False
        self._top_element = None

        for element in self.elements_ordered.reversed:
            if element.intersecting_mouse:
                self._intersecting_mouse = True
                self._top_element = element
                break

        self._last_frame_update = self.game.flow.current_frame

    # def _update_groups(self) -> None:
    #     for group in self.groups:
    #         group.update()

    @property
    def top_element(self) -> UI_Element | None:
        if self._last_frame_update == self.game.flow.current_frame:
            return self._top_element

        self._update_runtime_information()
        return self._top_element

    @property
    def intersecting_mouse(self) -> bool:
        if self._last_frame_update == self.game.flow.current_frame:
            return self._intersecting_mouse

        self._update_runtime_information()
        return self._intersecting_mouse

    @staticmethod
    def _element_comparator(element: UI_Element) -> int:
        return element.layer

    def add_element(self, element: UI_Element) -> bool:
        if element.name in self.elements:
            return False

        self.elements[element.name] = element
        self.elements_ordered.add(element)

    def remove_element(self, element: UI_Element | str) -> None:
        if type(element) == str:
            if element not in self.elements:
                return

            self.elements_ordered.remove(self.elements[element])
            del self.elements[element]
            return

        if element.name not in self.elements:
            return

        self.elements_ordered.remove(element)
        del self.elements[element.name]

    def add_group(self, group: UI_Group) -> bool:
        if group.name in self.groups:
            return False

        self.groups[group.name] = group
        return True

    def remove_group(self, group: UI_Group) -> None:
        del self.groups[group.name]

    def position_display_to_sheet(self, position: DisplayPosition) -> UISheetPosition:
        if not self.in_world:
            return position - self.position

        return self.game.camera.position_display_to_world(position) - self.position

    def position_sheet_to_display(self, position: UISheetPosition) -> DisplayPosition:
        if not self.in_world:
            return position + self.position

        return self.game.camera.position_world_to_display(position - self.position)

    def blit(self):
        for element in self.elements_ordered:
            if not element.active:
                continue

            if not self.game.window.display_rect.colliderect(element.rect):
                continue

            element.blit()
