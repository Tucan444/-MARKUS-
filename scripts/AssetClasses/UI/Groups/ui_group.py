from scripts.GameTypes import UISheetVector


class UI_Group:
    def __init__(self, sheet: 'UI_Sheet', name: str):
        self.game = sheet.game
        self.ui_sheet: 'UI_Sheet' = sheet
        self.name = name

        self.elements: set['UI_Element'] = set()

    @property
    def group_json(self) -> dict:
        return {
            "type": "ui group",
            "name": self.name,
            "elements": [element.group for element in self.elements]
        }

    @property
    def as_json(self) -> dict:
        return self.group_json

    @property
    def as_string(self) -> str:
        return (f"name: {self.name}, sheet name: {self.ui_sheet.name}, "
                f"number of elements: {len(self.elements)}")

    def __repr__(self):
        return self.as_string

    def __str__(self):
        return self.as_string

    @property
    def clone(self) -> 'UI_Group':
        return self.game.utilities.load_group(self.as_json, self.game, self.ui_sheet)

    @property
    def num_elements(self) -> int:
        return len(self.elements)

    @property
    def active_count(self) -> int:
        counter: int = 0

        for element in self.elements:
            if element.active:
                counter += 1

        return counter

    def set_active(self, active: bool) -> None:
        for element in self.elements:
            element.active = active

    def clear_callbacks(self) -> None:
        for element in self.elements:
            element.clear_callbacks()

    def detach(self) -> None:
        for element in self.elements:
            element.detach()

    def clear(self) -> None:
        self.elements = set()

    def move_elements(self, vector: UISheetVector):
        for element in self.elements:
            element.position += vector
