from scenes.scene_behaviour import SceneBehaviour
from scripts.AssetClasses.UI.ui_sheet import UI_Sheet
from scripts.GameTypes import SortableFunction


# reload by pressing space
# change self.sheet_name to change sheet
class UI_Editor(SceneBehaviour):
    def __init__(self, game, scene, active, order):
        super().__init__(game, scene, active, order)

        self.sheet_name: str = "test"
        self.fill_progress_bars: bool = True

        self.sheet: UI_Sheet = None
        self.reload_funka: SortableFunction = None

    def init(self):
        self.sheet = self.game.assets.ui_sheets[self.sheet_name]
        self.sheet.active = True
        self.reload_funka: SortableFunction = (
            0, f"reload sheet, {self.sheet.group}", self.reload_sheet, self.scene
        )

        self.game.inputs.on_space_press.add(self.reload_funka)

    def update(self):
        self.sheet.blit()

        if not self.fill_progress_bars:
            return

        for element in self.sheet.elements_ordered:
            if type(element).__name__ == "ProgressBar":
                element.add_progress_ranged(self.game.flow.dt)

    def end(self):
        pass

    def reload_sheet(self) -> None:
        self.sheet.reload()
