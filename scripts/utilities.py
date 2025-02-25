import importlib
import inspect
import pygame.image
import re
from pygame import Vector2, Surface

from scripts.AssetClasses.Tilemap.Tiles.animated_tile import AnimatedTile
from scripts.AssetClasses.Tilemap.Tiles.tile_component import TileComponent
from scripts.AssetClasses.UI.ui_sheet import UI_Sheet
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
from scripts.AssetClasses.Animation.animation import Animation
from scripts.AssetClasses.scene import Scene
from scenes.scene_behaviour import SceneBehaviour
from scripts.AssetClasses.Tilemap.tilemap import Tilemap
from scripts.AssetClasses.Tilemap.grid import Grid
from scripts.AssetClasses.Tilemap.Tiles.tile import Tile
from scripts.DataStructures.sorted_array import SortedArray
from scripts.GameTypes import WorldPosition, TilePosition, Color, HitboxType, Position, OffgridTilePosition
import os
import json

from scripts.Utilities.component import Component


class Utilities:
    DEFAULT_IMAGE_PATH: str="images"
    DEFAULT_SOUND_PATH: str= "sounds"
    DEFAULT_FONT_PATH: str = "fonts"
    DEFAULT_ANIMATION_PATH: str= "animations"
    DEFAULT_SCENE_PATH: str="scenes"
    DEFAULT_TILEMAP_PATH: str="tilemaps"
    DEFAULT_UI_SHEET_PATH: str="ui_sheets"

    DEFAULT_SHADER_PATH: str="shaders"

    def __init__(self, game: 'Game'):
        self.game: 'Game' = game
        self.print_callbacks: bool = False

        self.camel_case_pattern = re.compile(r'(?<!^)(?=[A-Z])')

    def init(self) -> None:
        pass

    def update(self) -> None:
        pass

    def end(self) -> None:
        pass

    @property
    def as_string(self) -> str:
        return ""

    def __repr__(self):
        return self.as_string

    def __str__(self):
        return self.as_string

    @staticmethod
    def call_functions(functions: SortedArray, args: list|None=None) -> None:
        if args is None:
            args = []

        for function_ in functions:
            if len(function_) == 4 and not function_[3].active:
                continue

            function_[2](*args)

    @staticmethod
    def collide_point(hitbox_type: HitboxType, rect: pygame.Rect, point: Position) -> bool:
        if hitbox_type == HitboxType.RECTANGLE:
            return rect.collidepoint(*point)

        elif hitbox_type == HitboxType.ELLIPSE:
            rect_size: Position = Vector2(rect.size)
            center: Position = Vector2(
                rect.x + (rect_size[0] * 0.5),
                rect.y + (rect_size[1] * 0.5)
            )
            point_centered: Position = point - center
            point_centered[0] *= rect_size[1] / rect_size[0]
            return point_centered.length_squared() < (rect_size[1] * 0.5) ** 2

        elif hitbox_type == HitboxType.CIRCLE:
            rect_size: Position = Vector2(rect.size)
            center: Position = Vector2(
                rect.x + (rect_size[0] * 0.5),
                rect.y + (rect_size[1] * 0.5)
            )
            magnitude: float = (point - center).length_squared()
            return magnitude < (rect_size[1] * 0.5) ** 2

    @staticmethod
    def snake_to_camel_case(string: str) -> str:
        return "".join([word.capitalize() for word in string.split("_")])

    def camel_to_snake_case(self, string: str) -> str:
        return self.camel_case_pattern.sub("_", string).lower()

    @staticmethod
    def color_swap(image: Surface, old_color: Color, new_color: Color, inplace: bool=False) -> Surface:
        new_image: Surface = Surface(image.get_size())
        new_image.fill(new_color)

        previous_colorkey: Color|None = image.get_colorkey()
        image.set_colorkey(old_color)
        new_image.blit(image, (0, 0))

        if not inplace:
            new_image.set_colorkey(previous_colorkey)
            return new_image

        image.blit(new_image, (0, 0))
        image.set_colorkey(previous_colorkey)
        return image

    @staticmethod
    def load_image(path: str, colorkey: Color = (0, 0, 0)) -> pygame.Surface:
        img: pygame.Surface = pygame.image.load(Utilities.DEFAULT_IMAGE_PATH + "/" + path).convert()
        img.set_colorkey(colorkey)
        return img

    @staticmethod
    def load_sound(path: str, default_volume: float = 0.5) -> pygame.mixer.Sound:
        sound: pygame.mixer.Sound = pygame.mixer.Sound(Utilities.DEFAULT_SOUND_PATH + "/" + path)
        sound.set_volume(default_volume)
        return sound

    @staticmethod
    def load_font(path: str) -> pygame.font.Font:
        local_path: str = f"{Utilities.DEFAULT_FONT_PATH}/{path}"
        font: pygame.font.Font = pygame.font.Font(local_path)
        return font

    @staticmethod
    def load_animation(path_to_folder: str, game: 'Game') -> Animation:
        original_image_path: str = Utilities.DEFAULT_IMAGE_PATH
        Utilities.DEFAULT_IMAGE_PATH = Utilities.DEFAULT_ANIMATION_PATH

        framePairs: list[tuple[int, pygame.Surface]] = []
        metadata: dict = {}

        for file in os.listdir(f"{Utilities.DEFAULT_ANIMATION_PATH}/{path_to_folder}"):
            if "__" in file:
                continue

            if file[-5:] == ".json":
                with open(f"{Utilities.DEFAULT_ANIMATION_PATH}/{path_to_folder}/{file}", "r") as f:
                    metadata = json.load(f)

                keys: set[str] = set(metadata.keys())
                assert("name" in keys)
                assert("loop" in keys)
                assert("pong" in keys)
                assert("reversed" in keys)
                assert("flip_x" in keys)
                assert("flip_y" in keys)
                assert("generate_flipped" in keys)
                assert("frame_durations" in keys)

            if file[-4:] == ".png" or file[-4:] == ".jpg":
                order: int = int(file.split(".")[0].split("_")[-1])
                framePairs.append( (order, Utilities.load_image(f"{path_to_folder}/{file}")) )

        framePairs.sort(key=lambda x: x[0])

        frames: list[pygame.Surface] = [pair[1] for pair in framePairs]

        animation: Animation = Animation(game, frames, metadata["name"],
                                   metadata["frame_durations"], metadata["loop"], metadata["pong"],
                                   metadata["reversed"], metadata["flip_x"], metadata["flip_y"])

        if metadata["generate_flipped"]:
            animation.generate_flipped()

        Utilities.DEFAULT_IMAGE_PATH = original_image_path

        return animation

    @staticmethod
    def try_load_components(path_to_file: str) -> list[type(Component)]:
        script = path_to_file.replace("/", ".")[:-3]  # components.my_special_component
        module = importlib.import_module(script)
        classes: list[tuple[str, type(object)]] = inspect.getmembers(module, predicate=inspect.isclass)
        classes = [(name, cls) for name, cls in classes if cls.__module__ == module.__name__]

        components: list[type(Component)] = []

        for class_ in classes:
            if not issubclass(class_[1], Component):
                continue

            components.append(class_[1])

        return components

    @staticmethod
    def load_scene(path_to_folder: str, game: 'Game') -> Scene:
        local_path: str = f"{Utilities.DEFAULT_SCENE_PATH}/{path_to_folder}"

        metadata: dict = {}
        scripts: list[str] = []
        dirs_to_do: set[str] = set()

        for file in os.listdir(local_path):
            if "__" in file:
                continue

            if file[-5:] == ".json":
                with open(f"{local_path}/{file}", "r") as f:
                    metadata = json.load(f)

                keys: set[str] = set(metadata.keys())
                assert ("name" in keys)
                assert ("active" in keys)
                assert ("active scripts" in keys)

            elif file[-3:] == ".py":
                scripts.append(f"{local_path}/{file}")
            elif "." not in file:
                dirs_to_do.add(f"{local_path}/{file}")

        to_clear: list[str] = []
        to_add: list[str] = []
        while dirs_to_do:
            to_clear += dirs_to_do

            for dir_ in dirs_to_do:
                for file in os.listdir(dir_):
                    if "__" in file:
                        continue

                    if file[-3:] == ".py":
                        scripts.append(f"{dir_}/{file}")
                    elif "." not in file:
                        to_add.append(f"{dir_}/{file}")

            for item in to_clear:
                dirs_to_do.remove(item)

            for item in to_add:
                dirs_to_do.add(item)

            to_clear = []
            to_add = []

        # we have scene json loaded in metadata
        # we have script names loaded in scripts

        if "execution order" not in metadata:
            metadata["execution order"] = {}

        if "order" not in metadata:
            metadata["order"] = 0

        scene: Scene = Scene(game, metadata["name"], metadata["active"], metadata["order"], local_path)
        objects: dict[str, SceneBehaviour] = {}
        objects_ordered: list[SceneBehaviour] = []
        classes_for_scene: dict[str, type(object)] = {}

        for script in scripts:
            script_name: str = script.split("/")[-1]  # test.py

            script = script.replace("/", ".")[:-3] # scenes.test_scene.test
            module = importlib.import_module(script)
            classes: list[tuple[str, type(object)]] = inspect.getmembers(module, predicate=inspect.isclass)
            classes = [(name, cls) for name, cls in classes if cls.__module__ == module.__name__]

            script_is_active: bool = script_name in metadata["active scripts"]
            order: int = metadata["execution order"][script_name] \
                if script_name in metadata["execution order"] else 0

            for class_ in classes:
                if class_[0] == "SceneBehaviour":
                    continue

                classes_for_scene[class_[0]] = class_[1]

                if not issubclass(class_[1], SceneBehaviour):
                    continue

                classInstance: SceneBehaviour = class_[1](game, scene, script_is_active, order)

                objects[class_[0]] = classInstance
                objects_ordered.append(classInstance)

        objects_ordered.sort(key=lambda x: x.order)

        scene.objects = objects
        scene.objects_ordered = objects_ordered
        scene.classes = classes_for_scene

        return scene

    @staticmethod
    def load_tilemap(path_to_file: str, game: 'Game') -> Tilemap:
        local_path: str = f"{Utilities.DEFAULT_TILEMAP_PATH}/{path_to_file}"

        tilemap_data: dict = {}
        with open(local_path, 'r') as f:
            tilemap_data = json.load(f)

            assert("name" in tilemap_data)
            assert("standard tile size" in tilemap_data)
            assert("alpha" in tilemap_data)
            assert("position" in tilemap_data)
            assert("grids" in tilemap_data)

        return game.utilities.load_tilemap_from_data(tilemap_data, local_path, game)

    @staticmethod
    def load_tilemap_from_data(tilemap_data: dict, local_path: str, game: 'Game') -> Tilemap:
        position: WorldPosition = pygame.math.Vector2(
            tilemap_data["position"][0],
            tilemap_data["position"][1]
        )

        tilemap: Tilemap = Tilemap(game, tilemap_data["name"], local_path,
                                   tilemap_data["standard tile size"], position, tilemap_data["alpha"])

        for grid_data in tilemap_data["grids"]:
            new_grid: Grid = Utilities.load_grid(grid_data, tilemap)

            tilemap.grids[new_grid.name] = new_grid
            tilemap.grids_ordered.append(new_grid)

        tilemap.grids_ordered.sort(key=lambda x: x.layer)
        return tilemap

    @staticmethod
    def load_grid(grid_data: dict, tilemap: Tilemap) -> Grid:
        assert("name" in grid_data)
        assert("tile size" in grid_data)
        assert("layer" in grid_data)
        assert("active" in grid_data)
        assert("depth" in grid_data)
        assert("use depth" in grid_data)
        assert("invisible" in grid_data)
        assert("physical" in grid_data)
        assert("tiles" in grid_data)
        assert("offgrid background" in grid_data)
        assert("offgrid foreground" in grid_data)
        assert("alpha" in grid_data)
        assert("ongrid padding" in grid_data)

        grid: Grid = Grid(tilemap, grid_data["name"], grid_data["tile size"],
                          grid_data["layer"], grid_data["active"],
                          grid_data["depth"], grid_data["use depth"],
                          grid_data["invisible"], grid_data["physical"],
                          grid_data["alpha"], grid_data["ongrid padding"])

        for tile_data in grid_data["tiles"]:
            new_tile: Tile = Utilities.load_tile(tile_data, grid, False)

            grid.tiles[new_tile.position] = new_tile

        for tile_data in grid_data["offgrid background"]:
            new_tile: Tile = Utilities.load_tile(tile_data, grid, True)

            grid.offgrid_background.add(new_tile)

        for tile_data in grid_data["offgrid foreground"]:
            new_tile: Tile = Utilities.load_tile(tile_data, grid, True)

            grid.offgrid_foreground.add(new_tile)

        return grid

    @staticmethod
    def load_tile(tile_data: dict, grid: Grid, is_offgrid: bool) -> Tile:
        assert("position" in tile_data) # position

        if "alpha" not in tile_data:
            tile_data["alpha"] = 1

        if "clone_animation" not in tile_data:
            tile_data["clone_animation"] = False

        tilemap: Tilemap = grid.tilemap
        game: 'Game' = tilemap.game
        is_image_tile: bool = "image" in tile_data

        image: pygame.Surface | None = None
        if is_image_tile:
            image = Utilities._load_tile_image(tile_data, grid, is_offgrid)

        animation: Animation | None = None
        if not is_image_tile:
            assert "animation" in tile_data
            animation = Utilities._load_tile_animation(tile_data, grid, is_offgrid)

        positionAsStrings: list[str] = tile_data["position"].split(";")
        assert(len(positionAsStrings) == 2)
        if is_offgrid:
            position: OffgridTilePosition = (float(positionAsStrings[0]), float(positionAsStrings[1]))
        else:
            position: TilePosition = (int(positionAsStrings[0]), int(positionAsStrings[1]))

        tile_groups: set[str] = set(tile_data["groups"]) if "groups" in tile_data else set()
        components: list[TileComponent] = []

        if is_image_tile:
            assert image is not None
            tile: Tile = Tile(grid, image, position, is_offgrid, tile_data["alpha"], tile_groups)
        else:
            assert animation is not None
            tile: AnimatedTile = AnimatedTile(grid, animation, position, is_offgrid, tile_data["clone_animation"],
                                              tile_data["alpha"], tile_groups)

        if "components" in tile_data:
            for component_data in tile_data["components"]:
                component: TileComponent = game.assets.components[component_data["class_name"]].load(component_data, tile)
                components.append(component)

        tile.components = components

        for tile_group in tile_groups:
            if tile_group not in tilemap.tile_groups:
                tilemap.tile_groups[tile_group] = set()

            tilemap.tile_groups[tile_group].add(tile)

        return tile

    @staticmethod
    def _load_tile_image(tile_data: dict, grid: Grid, offgrid: bool) -> pygame.Surface:
        if offgrid:
            return grid.game.assets.images[tile_data["image"]]

        grid.rescale_image_for_grid(tile_data["image"])
        return grid.get_image(tile_data["image"])

    @staticmethod
    def _load_tile_animation(tile_data: dict, grid: Grid, offgrid: bool) -> Animation:
        if offgrid:
            grid.tilemap.clone_animation_for_tilemap(tile_data["animation"])
            return grid.tilemap.get_cloned_animation(tile_data["animation"])

        grid.rescale_animation_for_grid(tile_data["animation"])
        return grid.get_animation(tile_data["animation"])

    @staticmethod
    def load_ui_sheet(path_to_file: str, game: 'Game') -> UI_Sheet:
        local_path: str = f"{Utilities.DEFAULT_UI_SHEET_PATH}/{path_to_file}"

        sheet_data: dict = {}
        with open(local_path, 'r') as f:
            sheet_data= json.load(f)

            assert "type" in sheet_data
            assert "name" in sheet_data
            assert "position" in sheet_data
            assert len(sheet_data["position"]) == 2
            assert "in world" in sheet_data
            assert "elements" in sheet_data
            assert "groups" in sheet_data

        return game.utilities.load_ui_sheet_from_data(sheet_data, local_path, game)

    @staticmethod
    def load_ui_sheet_from_data(sheet_data: dict, local_path: str, game: 'Game') -> UI_Sheet:
        sheet: UI_Sheet = UI_Sheet(game, sheet_data["name"], local_path,
                                   Vector2(*sheet_data["position"]), sheet_data["in world"])

        # DEPT we have 2 groups, might need whole sort system if it gets worse in future
        load_later: list['UI_Element'] = []

        # loading first
        for element_data in sheet_data["elements"]:
            if element_data["type"] == "scroll zone":
                load_later.append(element_data)
                continue

            element: 'UI_Element' = Utilities.load_ui_element(element_data, game, sheet)

            if element is not None:
                sheet.add_element(element)
            else:
                print(f"[LOG] element got back none, its data: {element_data}")

        # loading later
        for element_data in load_later:
            element: 'UI_Element' = Utilities.load_ui_element(element_data, game, sheet)

            if element is not None:
                sheet.add_element(element)
            else:
                print(f"[LOG] element got back none, its data: {element_data}")

        # loading groups
        for group_data in sheet_data["groups"]:
            group: UI_Group = Utilities.load_group(group_data, game, sheet)

            if group is not None:
                sheet.add_group(group)
            else:
                print(f"[LOG] group got back none, its data: {group_data}")

        return sheet

    @staticmethod
    def load_ui_element(element_data: dict, game: 'Game', sheet: UI_Sheet) -> 'UI_Element':
        assert "type" in element_data
        assert element_data["type"] != "ui element"
        assert "size" in element_data
        assert len(element_data["size"]) == 2
        assert "name" in element_data
        assert "position" in element_data
        assert len(element_data["position"]) == 2
        assert "layer" in element_data
        assert "input wait" in element_data
        assert "active" in element_data
        assert "hitbox type" in element_data

        type_: str =  element_data["type"]
        element: 'UI_Element' = None

        if type_ == "toggle":
            element = Utilities.load_toggle(element_data, game, sheet)
        elif type_ == "text":
            element = Utilities.load_text(element_data, game, sheet)
        elif type_ == "slider":
            element = Utilities.load_slider(element_data, game, sheet)
        elif type_ == "progress bar":
            element = Utilities.load_progress_bar(element_data, game, sheet)
        elif type_ == "image":
            element = Utilities.load_image_ui(element_data, game, sheet)
        elif type_ == "button":
            element = Utilities.load_button(element_data, game, sheet)
        elif type_ == "dropdown":
            element = Utilities.load_dropdown(element_data, game, sheet)
        elif type_ == "scroll zone":
            element = Utilities.load_scroll_zone(element_data, game, sheet)

        return element

    @staticmethod
    def load_toggle(data: dict, game: 'Game', sheet: UI_Sheet) -> Toggle:
        images = game.assets.images

        toggle: Toggle = Toggle(
            game, sheet, data["name"], Vector2(*data["position"]), data["layer"], data["active"],
            data["input wait"], data["is_on"], data["enabled"], HitboxType(data["hitbox type"]), images[data["on image"]],
            images[data["off image"]], images[data["on image disabled"]], images[data["off image disabled"]],
            images[data["on image hover"]], images[data["off image hover"]]
        )

        return toggle

    @staticmethod
    def load_text(data: dict, game: 'Game', sheet: UI_Sheet) -> Text:
        text: Text = Text(
            game, sheet, tuple(data["size"][:2]), data["name"], Vector2(*data["position"]),
            data["layer"], data["active"], data["text"], tuple(data["color idle"][:3]),
            tuple(data["color hover"][:3]), tuple(data["color pressed"][:3]), data["is interactive"],
            game.assets.fonts[data["font"]], data["font size"], data["bold"], data["centered"],
            data["visualize boundary"]
        )

        return text

    @staticmethod
    def load_slider(data: dict, game: 'Game', sheet: UI_Sheet) -> Slider:
        images = game.assets.images

        slider: Slider = Slider(
            game, sheet, data["name"], Vector2(*data["position"]), data["layer"], data["active"],
            data["input wait"], data["min value"], data["max value"], data["initial value"],
            data["whole numbers"], data["enabled"], HitboxType(data["knob hitbox type"]),
            HitboxType(data["slider hitbox type"]), images[data["slider"]], images[data["slider filled"]],
            images[data["knob"]], images[data["knob hover"]], images[data["knob pressed"]],
            images[data["knob disabled"]]
        )

        return slider

    @staticmethod
    def load_progress_bar(data: dict, game: 'Game', sheet: UI_Sheet) -> ProgressBar:
        images = game.assets.images

        progress_bar: ProgressBar = ProgressBar(
            game, sheet, data["name"], Vector2(*data["position"]), data["layer"], data["active"],
            HitboxType(data["hitbox type"]), images[data["empty"]], images[data["full"]], data["horizontal"],
            data["flip direction"], data["progress"], data["progress range"]
        )

        return progress_bar

    @staticmethod
    def load_image_ui(data: dict, game: 'Game', sheet: UI_Sheet) -> Image:
        images = game.assets.images

        image: Image = Image(
            game, sheet, data["name"], Vector2(*data["position"]), data["layer"], data["active"],
            HitboxType(data["hitbox type"]), images[data["image"]], images[data["image hover"]]
        )

        return image

    @staticmethod
    def load_button(data: dict, game: 'Game', sheet: UI_Sheet) -> Button:
        images = game.assets.images

        button: Button = Button(
            game, sheet, data["name"], Vector2(*data["position"]), data["layer"], data["active"],
            data["input wait"], data["enabled"], HitboxType(data["hitbox type"]),
            images[data["idle image"]], images[data["hover image"]], images[data["pressed image"]],
            images[data["disabled image"]]
        )

        return button

    @staticmethod
    def load_dropdown(data: dict, game: 'Game', sheet: UI_Sheet) -> Dropdown:
        images = game.assets.images
        fonts = game.assets.fonts

        dropdown: Dropdown = Dropdown(
            game, sheet, data["name"], Vector2(*data["position"]), data["layer"], data["active"],
            data["input wait"], HitboxType(data["selection hitbox type"]),
            HitboxType(data["option hitbox type"]), data["selection text"], data["use option as text"],
            data["text padding"], data["options"], data["initial option"], data["enabled"],
            images[data["selection"]], images[data["selection hover"]], images[data["selection selected"]],
            images[data["selection disabled"]], images[data["option"]], images[data["option hover"]],
            fonts[data["selection font"]], data["selection font size"], data["selection bold"],
            fonts[data["option font"]], data["option font size"], data["option bold"],
            tuple(data["color selection"][:3]), tuple(data["color selection hover"][:3]),
            tuple(data["color selection pressed"][:3]), tuple(data["color option"][:3]),
            tuple(data["color option hover"][:3]), images[data["options background"]],
            images[data["options foreground"]], data["scroll speed"]
        )

        return dropdown

    @staticmethod
    def load_scroll_zone(data: dict, game: 'Game', sheet: UI_Sheet) -> ScrollZone:
        assert len(data["scroll bounds"]) == 2
        images = game.assets.images

        scroll_zone: ScrollZone = ScrollZone(
            game, sheet, data["name"], Vector2(*data["position"]), data["layer"], data["active"],
            HitboxType(data["hitbox type"]), data["input wait"], data["enabled"],
            images[data["image"]], images[data["image hover"]], images[data["image disabled"]],
            data["scroll speed"], [Vector2(*bound) for bound in data["scroll bounds"]],
            data["vertical"], data["flip direction"]
        )

        for element_name in data["zone elements"]:
            scroll_zone.add_element(sheet.elements[element_name])

        return scroll_zone

    @staticmethod
    def load_group(group_data: dict, game: 'Game', sheet: UI_Sheet) -> UI_Group | None:
        assert "type" in group_data
        assert "name" in group_data
        assert "elements" in group_data

        type_: str = group_data["type"]
        group: UI_Group | None = None

        if type_ == "ui group":
            group = Utilities.load_ui_group(group_data, sheet)
        elif type_ == "select group":
            group = Utilities.load_ui_select_group(group_data, sheet)

        return group

    @staticmethod
    def load_ui_group(data: dict, sheet: UI_Sheet) -> UI_Group:
        group: UI_Group = UI_Group(sheet, data["name"])

        for element in data["elements"]:
            group.elements.add(sheet.elements[element])

        return group

    @staticmethod
    def load_ui_select_group(data: dict, sheet: UI_Sheet) -> UI_Group:
        group: UI_SelectGroup = UI_SelectGroup(
            sheet, data["name"], data["max count"], data["limit off toggles"], data["always selectable"]
        )

        for element in data["elements"]:
            group.add_toggle(sheet.elements[element])

        return group
