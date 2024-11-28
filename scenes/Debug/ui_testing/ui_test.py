from pygame import Vector2
from scenes.scene_behaviour import SceneBehaviour
from scripts.AssetClasses.UI.Groups.ui_group import UI_Group
from scripts.AssetClasses.UI.Groups.ui_select_group import UI_SelectGroup
from scripts.AssetClasses.UI.dropdown import Dropdown
from scripts.AssetClasses.UI.progress_bar import ProgressBar
from scripts.AssetClasses.UI.scroll_zone import ScrollZone
from scripts.AssetClasses.UI.slider import Slider
from scripts.AssetClasses.UI.toggle import Toggle
from scripts.AssetClasses.UI.image import Image
from scripts.AssetClasses.UI.button import Button
from scripts.AssetClasses.UI.text import Text
from scripts.AssetClasses.UI.ui_sheet import UI_Sheet
from scripts.GameTypes import HitboxType, SortableFunction


class UI_Test(SceneBehaviour):
    def __init__(self, game, scene, active, order):
        super().__init__(game, scene, active, order)
        self.name = "A"

        # self.monstrosity()
        self.sheet: UI_Sheet = None
        self.reload_funka: SortableFunction = None


    def init(self):
        self.sheet = self.game.assets.ui_sheets["test"]
        self.reload_funka: SortableFunction = (
            0, f"reload sheet, {self.sheet.group}", self.reload_sheet, self.scene
        )
        self.game.inputs.on_space_press.add(self.reload_funka)

    def update(self):
        self.sheet.blit()
        #self.progress_bar.add_progress(self.game.flow.dt)
        #self.progress_bar.add_progress_ranged(self.game.flow.dt * 8)
        #self.group.move_elements(Vector2(self.game.flow.dt * 10, self.game.flow.dt * 5))
        #print(self.sheet.intersecting_mouse)

        #self.scroll_zone.position = self.scroll_zone.position + Vector2(self.game.flow.dt * 10, 0)
        #self.scroll_zone.move_with_elements(Vector2(0, self.game.flow.dt * 20))

    def end(self):
        pass

    def reload_sheet(self) -> None:
        self.sheet.reload()

    def monstrosity(self) -> None:
        self.sheet: UI_Sheet = UI_Sheet(self.game, "test",
                                        f"{self.game.utilities.DEFAULT_UI_SHEET_PATH}/test_ui_sheet.json",
                                        Vector2(100, 100))
        # for i in range(2000):
        self.text: Text = Text(self.game, self.sheet, (500, 100), f"bla", Vector2(0, 0),
                               5, True,
                               "KILL YOURSELF", (255, 0, 0), (0, 255, 0),
                               (0, 0, 255), True,
                               self.game.assets.fonts["Helvetica-Bold"],
                               20, True, True, True)
        self.sheet.add_element(self.text)

        # for i in range(5000):
        self.button: Button = Button(self.game, self.sheet, f"guh", Vector2(600, 0),
                                     2, True, -45, True, HitboxType.RECTANGLE,
                                     self.game.assets.images["tile"], self.game.assets.images["tileHovered"],
                                     self.game.assets.images["tilePressed"], self.game.assets.images["tileDisabled"])
        self.sheet.add_element(self.button)

        self.button2: Button = Button(self.game, self.sheet, f"guha", Vector2(-100, -100),
                                      -5, True, -40, True, HitboxType.ELLIPSE,
                                      self.game.assets.images["cell2"], self.game.assets.images["cell2Hover"],
                                      self.game.assets.images["cell2"], self.game.assets.images["cell2Hover"])
        self.sheet.add_element(self.button2)

        self.image: Image = Image(self.game, self.sheet, "FUKA", Vector2(100, 0), -4, True,
                                  HitboxType.RECTANGLE, self.game.assets.images["0"], self.game.assets.images["0"])
        self.sheet.add_element(self.image)

        self.toggle: Toggle = Toggle(self.game, self.sheet, "Himeko", Vector2(150, 200),
                                     6, True, -50, True, True, HitboxType.CIRCLE,
                                     self.game.assets.images["tile"], self.game.assets.images["tileDisabled"],
                                     self.game.assets.images["tileHovered"], self.game.assets.images["tilePressed"],
                                     self.game.assets.images["tilePressed"], self.game.assets.images["tileHovered"])
        self.sheet.add_element(self.toggle)

        self.toggle2: Toggle = Toggle(self.game, self.sheet, "Himeko Vermilion Knight", Vector2(165, 210),
                                      5, True, -50, True, True, HitboxType.CIRCLE,
                                      self.game.assets.images["tile"], self.game.assets.images["tileDisabled"],
                                      self.game.assets.images["tileHovered"], self.game.assets.images["tilePressed"],
                                      self.game.assets.images["tilePressed"], self.game.assets.images["tileHovered"])
        self.sheet.add_element(self.toggle2)

        self.toggle3: Toggle = Toggle(self.game, self.sheet, "Himeko x Kiana", Vector2(185, 210),
                                      5, True, -50, True, True, HitboxType.CIRCLE,
                                      self.game.assets.images["tile"], self.game.assets.images["tileDisabled"],
                                      self.game.assets.images["tileHovered"], self.game.assets.images["tilePressed"],
                                      self.game.assets.images["tilePressed"], self.game.assets.images["tileHovered"])
        self.sheet.add_element(self.toggle3)

        self.slider: Slider = Slider(self.game, self.sheet, "Kiana", Vector2(200, -50),
                                     7, True, -50, 2.2, 3.6, 2.8,
                                     False, True, HitboxType.RECTANGLE, HitboxType.ELLIPSE,
                                     self.game.assets.images["slider"], self.game.assets.images["sliderFilled"],
                                     self.game.assets.images["tile"], self.game.assets.images["tileHovered"],
                                     self.game.assets.images["tilePressed"], self.game.assets.images["tileDisabled"])
        self.sheet.add_element(self.slider)

        self.progress_bar: ProgressBar = ProgressBar(self.game, self.sheet, "uga buga", Vector2(-50, 150),
                                                     6, True, HitboxType.RECTANGLE,
                                                     self.game.assets.images["slider"],
                                                     self.game.assets.images["sliderFilled"],
                                                     True, False, 0, 80)
        self.sheet.add_element(self.progress_bar)

        self.images = self.game.assets.images
        self.dropdown: Dropdown = Dropdown(self.game, self.sheet, "FU HUA", Vector2(200, 150), 9, True,
                                           -500, HitboxType.RECTANGLE, HitboxType.ELLIPSE,
                                           "suits", True, 0.1, [
                                               "casual", "shadow knight", "phoenix", "emperor", "herreser of vermilion",
                                               "bed", "sexy"
                                           ], 1, True, self.game.assets.images["sliderFilled"],
                                           self.game.assets.images["sliderHover"], self.images["slider"],
                                           self.game.assets.images["sliderDisabled"], self.images["option"],
                                           self.images["option_hover"],
                                           self.game.assets.fonts["Helvetica-Bold"], 20, True,
                                           self.game.assets.fonts["Helvetica-Bold"], 10, False, (250, 250, 250),
                                           (150, 150, 150), (50, 50, 50),
                                           (255, 150, 150), (255, 200, 200),
                                           self.images["bg"], self.images["fg"], 0.2)
        self.sheet.add_element(self.dropdown)

        self.group: UI_Group = UI_Group(self.sheet, "toggles movers")

        self.group.elements.add(self.dropdown)
        self.group.elements.add(self.button)
        self.group.elements.add(self.button2)
        self.group.elements.add(self.progress_bar)
        self.group.elements.add(self.slider)
        self.group.elements.add(self.text)
        self.group.elements.add(self.toggle)
        self.group.elements.add(self.toggle2)
        self.group.elements.add(self.toggle3)
        self.sheet.add_group(self.group)

        self.select_group: UI_SelectGroup = UI_SelectGroup(self.sheet, "oh god work",
                                                           2, False)

        self.select_group.add_toggle(self.toggle)
        self.select_group.add_toggle(self.toggle2)
        self.select_group.add_toggle(self.toggle3)
        self.sheet.add_group(self.select_group)

        self.scroll_zone: ScrollZone = ScrollZone(self.game, self.sheet, "Theresa", Vector2(700, 0),
                                                  3, True, HitboxType.RECTANGLE, -4, True,
                                                  self.images["slider"], self.images["sliderFilled"],
                                                  self.images["sliderDisabled"],
                                                  2, (Vector2(0, 100), Vector2(-10, 50)),
                                                  True, False)

        self.scroll_zone.add_elements(self.slider, self.progress_bar)
        self.scroll_zone.add_element(self.button)
        self.sheet.add_element(self.scroll_zone)

        self.sheet.save(compact=False)
