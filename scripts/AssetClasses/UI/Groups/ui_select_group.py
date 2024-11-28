import copy

from scripts.AssetClasses.UI.Groups.ui_group import UI_Group
from scripts.AssetClasses.UI.toggle import Toggle
from scripts.GameTypes import SortableFunction


class UI_SelectGroup(UI_Group):
    def __init__(self, sheet: 'UI_Sheet', name: str, max_count: int, limit_off_toggles: bool=True,
                 always_selectable: bool=True):
        super().__init__(sheet, name)

        self.max_count: int = max_count
        self._limit_off_toggles: bool = limit_off_toggles
        self.always_selectable: bool = always_selectable

        self.toggles: set[Toggle] = set()
        # optimizable use ordered dict if causes performance problems
        self.selected_toggles: list[str] = []

        self.input_wait: float = -5_000_000.
        self.funka: SortableFunction = (self.input_wait, f"ui select group, {self.name}",
                                        self.handle_toggle_change)

    @property
    def as_json(self) -> dict:
        json_form: dict =  self.group_json

        json_form["type"] = "select group"
        json_form["max count"] = self.max_count
        json_form["limit off toggles"] = self.limit_off_toggles
        json_form["always selectable"] = self.always_selectable

        return json_form

    @property
    def as_string(self) -> str:
        return (f"name: {self.name}, sheet name: {self.ui_sheet.name}, "
                f"number of elements: {len(self.elements)}, "
                f"number of toggles: {len(self.toggles)}, max count: {self.max_count}, "
                f"counting off toggles: {self.limit_off_toggles}, "
                f"always selectable: {self.always_selectable}"
                f"number of selected toggles: {len(self.selected_toggles)}")

    def __repr__(self):
        return self.as_string

    def __str__(self):
        return self.as_string

    @property
    def limit_off_toggles(self) -> bool:
        return self._limit_off_toggles

    @limit_off_toggles.setter
    def limit_off_toggles(self, limit_off_toggles: bool) -> None:
        if limit_off_toggles is self._limit_off_toggles:
            return

        self._limit_off_toggles = limit_off_toggles

        toggles: set[Toggle] = copy.copy(self.toggles)
        self.toggles = set()
        self.selected_toggles = []

        for toggle in toggles:
            self.add_toggle(toggle)

    def add_toggle(self, toggle: Toggle) -> None:
        assert(type(toggle) == Toggle)

        self.elements.add(toggle)
        self.toggles.add(toggle)

        if self.toggle_selected(toggle):
            if len(self.selected_toggles) >= self.max_count:
                self.unselect_toggle(toggle)
            else:
                self.selected_toggles.append(toggle.name)

        toggle.invoke_on_toggle.add(self.funka)

    def remove_toggle(self, toggle: Toggle) -> None:
        assert(type(toggle) == Toggle)

        self.elements.remove(toggle)
        self.toggles.remove(toggle)

        if toggle.name in self.selected_toggles:
            self.selected_toggles.remove(toggle.name)

        toggle.invoke_on_toggle.remove(self.funka)

    def handle_toggle_change(self, toggle: Toggle) -> None:
        if self.toggle_selected(toggle):
            overflow: bool = len(self.selected_toggles) >= self.max_count
            if overflow and not self.always_selectable:
                self.unselect_toggle(toggle)
            elif overflow and self.always_selectable:
                self.selected_toggles.append(toggle.name)

                self.unselect_toggle(self.ui_sheet.elements[self.selected_toggles[0]])
                self.selected_toggles.remove(self.selected_toggles[0])
            else:
                self.selected_toggles.append(toggle.name)
        else:
            if toggle.name in self.selected_toggles:
                self.selected_toggles.remove(toggle.name)

    def toggle_selected(self, toggle: Toggle) -> bool:
        return toggle.is_on if not self.limit_off_toggles else not toggle.is_on

    def unselect_toggle(self, toggle: Toggle) -> None:
        if self.limit_off_toggles:
            toggle.is_on = True
        else:
            toggle.is_on = False

    def clear(self) -> None:
        for toggle in copy.copy(self.toggles):
            self.remove_toggle(toggle)

        self.elements = set()
