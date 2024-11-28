import pygame
import os

from scripts.AssetClasses.UI.ui_sheet import UI_Sheet
from scripts.AssetClasses.animation import Animation
from scripts.AssetClasses.Tilemap.tilemap import Tilemap
from scripts.GameTypes import Success
from scripts.Utilities.component import Component


class Assets:
    def __init__(self, game: 'Game', load_assets: bool=True, default_volume: float = 0.5):
        self.game: 'Game' = game

        # self.images has paths as keys, same with sounds
        # fonts have filenames without .ttf as keys
        # animations and tilemaps have defined names as keys

        self.images: dict[str, pygame.Surface] = {}
        self.sounds: dict[str, pygame.mixer.Sound] = {}
        self.fonts: dict[str, pygame.font.Font] = {}
        self.animations: dict[str, Animation] = {}
        self.components: dict[str, type(Component)] = {}

        self.image_names: dict[pygame.Surface, str] = {}
        self.sound_names: dict[pygame.mixer.Sound, str] = {}
        self.font_names: dict[pygame.font.Font, str] = {}
        self.animation_names: dict[Animation, str] = {}
        self.component_names: dict[type(Component), str] = {}

        self.tilemaps: dict[str, Tilemap] = {}
        self.ui_sheets: dict[str, UI_Sheet] = {}

        self.tilemap_names: dict[Tilemap, str] = {}
        self.ui_sheet_names: dict[UI_Sheet, str] = {}

        self.images_loaded: bool = False
        self.sounds_loaded: bool = False
        self.fonts_loaded: bool = False
        self.animations_loaded: bool = False
        self.components_loaded: bool = False

        self.tilemaps_loaded: bool = False
        self.ui_sheets_loaded: bool = False

        self.default_volume: float = default_volume
        self.load_assets: bool = load_assets

        if self.load_assets:
            self._load_images()
            self._load_sounds()
            self._load_fonts()
            self._load_animations()
            self._load_components()

            self._load_name_lookups()

    def init(self) -> None:
        if self.load_assets:
            self._load_tilemaps()
            self._load_ui_sheets()

    def update(self) -> None:
        pass

    def end(self) -> None:
        pass

    @property
    def as_string(self) -> str:
        return (f"number of images: {len(self.images)}, "
                f"number of animations: {len(self.animations)}, "
                f"number of sounds: {len(self.sounds)}, "
                f"number of fonts: {len(self.fonts)}, "
                f"number of components: {len(self.components)}"
                f"number of tilemaps: {len(self.tilemaps)}, "
                f"number of ui_sheets: {len(self.ui_sheets)}, "
                f"default volume: {self.default_volume}")

    def __repr__(self):
        return self.as_string

    def __str__(self):
        return self.as_string

    def _load_name_lookups(self) -> None:
        self.image_names = {
            image: name for name, image in self.images.items()
        }

        self.sound_names = {
            sound: name for name, sound in self.sounds.items()
        }

        self.font_names = {
            font: name for name, font in self.fonts.items()
        }

        self.animation_names = {
            animation: name for name, animation in self.animations.items()
        }

        self.component_names = {
            component: name for name, component in self.components.items()
        }

        self.tilemap_names = {
            tilemap: name for name, tilemap in self.tilemaps.items()
        }

        self.ui_sheet_names = {
            ui_sheet: name for name, ui_sheet in self.ui_sheets.items()
        }

    def load_image(self, path: str) -> Success:
        if path[:-4] in self.images:
            return False

        self.images[path[:-4]] = self.game.utilities.load_image(path)
        return True

    def load_sound(self, path: str) -> Success:
        if path[:-4] in self.sounds:
            return False

        self.sounds[path[:-4]] = self.game.utilities.load_sound(path, self.default_volume)
        return True

    def load_font(self, path_to_folder: str) -> Success:
        name: str = path_to_folder.split("/")[-1][:-4]
        if name in self.fonts:
            return False

        self.fonts[name] = self.game.utilities.load_font(path_to_folder)
        return True

    def load_animation(self, path_to_folder: str) -> Success:
        animation: Animation = self.game.utilities.load_animation(path_to_folder, self.game)

        if animation.name in self.animations:
            return False

        self.animations[animation.name] = animation

        return True

    def try_load_component(self, path_to_file: str) -> Success:
        components: list[type(Component)] = self.game.utilities.try_load_components(path_to_file)
        no_duplicates: bool = True

        for component in components:
            if component.__name__ in self.components:
                no_duplicates = False
                continue

            self.components[component.__name__] = component

        return no_duplicates

    def load_tilemap(self, path_to_folder: str) -> Success:
        tilemap: Tilemap = self.game.utilities.load_tilemap(path_to_folder, self.game)

        if tilemap.name in self.tilemaps:
            return False

        self.tilemaps[tilemap.name] = tilemap
        return True

    def load_ui_sheet(self, path_to_folder: str) -> Success:
        sheet: UI_Sheet = self.game.utilities.load_ui_sheet(path_to_folder, self.game)

        if sheet.name in self.ui_sheets:
            return False

        self.ui_sheets[sheet.name] = sheet
        return True

    def load_what_isnt_loaded(self) -> None:
        if not self.images_loaded:
            self._load_images()

        if not self.animations_loaded:
            self._load_animations()

        if not self.sounds_loaded:
            self._load_sounds()

        if not self.fonts_loaded:
            self._load_fonts()

        if not self.components_loaded:
            self._load_components()

        if not self.tilemaps_loaded:
            self._load_tilemaps()

        if not self.ui_sheets_loaded:
            self._load_ui_sheets()

    def _load_images(self) -> None:
        dirs_to_do: set[str] = set()

        for file in os.listdir(self.game.utilities.DEFAULT_IMAGE_PATH):
            if "__" in file:
                continue

            if file[-4:] == ".png" or file[-4:] == ".jpg":
                self.load_image(file)
            else:
                dirs_to_do.add(file)

        to_clear: list[str] = []
        to_add: list[str] = []
        while dirs_to_do:
            to_clear += dirs_to_do

            for dir_ in dirs_to_do:
                for file in os.listdir(f"{self.game.utilities.DEFAULT_IMAGE_PATH}/{dir_}"):
                    if "__" in file:
                        continue

                    if file[-4:] == ".png" or file[-4:] == ".jpg":
                        self.load_image(f"{dir_}/{file}")
                    else:
                        to_add.append(f"{dir_}/{file}")

            for item in to_clear:
                dirs_to_do.remove(item)

            for item in to_add:
                dirs_to_do.add(item)

            to_clear = []
            to_add = []

        self.images_loaded = True

    def _load_sounds(self) -> None:
        dirs_to_do: set[str] = set()

        for file in os.listdir(self.game.utilities.DEFAULT_SOUND_PATH):
            if "__" in file:
                continue

            if file[-4:] == ".wav":
                self.load_sound(file)
            elif file[-4:] == ".mp3":
                print(f"[LOG] found mp3 file, ignoring: {file}")
            else:
                dirs_to_do.add(file)

        to_clear: list[str] = []
        to_add: list[str] = []
        while dirs_to_do:
            to_clear += dirs_to_do

            for dir_ in dirs_to_do:
                for file in os.listdir(f"{self.game.utilities.DEFAULT_SOUND_PATH}/{dir_}"):
                    if "__" in file:
                        continue

                    if file[-4:] == ".wav":
                        self.load_sound(f"{dir_}/{file}")
                    elif file[-4:] == ".mp3":
                        print(f"[LOG] found mp3 file, ignoring: {dir_}/{file}")
                    else:
                        to_add.append(f"{dir_}/{file}")

            for item in to_clear:
                dirs_to_do.remove(item)

            for item in to_add:
                dirs_to_do.add(item)

            to_clear = []
            to_add = []

        self.sounds_loaded = True

    def _load_fonts(self) -> None:
        dirs_to_do: set[str] = set()

        for file in os.listdir(self.game.utilities.DEFAULT_FONT_PATH):
            if "__" in file:
                continue

            if file[-4:] == ".ttf":
                self.load_font(file)
            elif "." in file:
                continue
            else:
                dirs_to_do.add(file)

        to_clear: list[str] = []
        to_add: list[str] = []
        while dirs_to_do:
            to_clear += dirs_to_do

            for dir_ in dirs_to_do:
                for file in os.listdir(f"{self.game.utilities.DEFAULT_FONT_PATH}/{dir_}"):
                    if "__" in file:
                        continue

                    if file[-4:] == ".ttf":
                        self.load_font(f"{dir_}/{file}")
                    elif "." in file:
                        continue
                    else:
                        to_add.append(f"{dir_}/{file}")

            for item in to_clear:
                dirs_to_do.remove(item)

            for item in to_add:
                dirs_to_do.add(item)

            to_clear = []
            to_add = []

        self.fonts_loaded = True

    def _load_animations(self) -> None:
        dirs_to_do: set[str] = set()

        for file in os.listdir(self.game.utilities.DEFAULT_ANIMATION_PATH):
            if "__" in file:
                continue

            if "." in file:
                continue
            else:
                dirs_to_do.add(file)

        to_clear: list[str] = []
        to_add: list[str] = []
        while dirs_to_do:
            to_clear += dirs_to_do

            for dir_ in dirs_to_do:
                inside: list[str] = os.listdir(f"{self.game.utilities.DEFAULT_ANIMATION_PATH}/{dir_}")
                found_animation: bool = False
                for file in inside:
                    if "__" in file:
                        continue

                    if file[-5:] == ".json":
                        found_animation = True
                        break

                if found_animation:
                    self.load_animation(dir_)
                    continue

                for file in inside:
                    if "__" in file:
                        continue

                    to_add.append(f"{dir_}/{file}")

            for item in to_clear:
                dirs_to_do.remove(item)

            for item in to_add:
                dirs_to_do.add(item)

            to_clear = []
            to_add = []

        self.animations_loaded = True

    def _load_components(self) -> None:
        dirs_to_do: set[str] = set()

        for file in os.listdir():
            if "__" in file:
                continue

            if file[-3:] == ".py":
                self.try_load_component(file)
            elif "." in file or file == "_trash":
                continue
            else:
                dirs_to_do.add(file)

        to_clear: list[str] = []
        to_add: list[str] = []
        while dirs_to_do:
            to_clear += dirs_to_do

            for dir_ in dirs_to_do:
                for file in os.listdir(dir_):
                    if "__" in file:
                        continue

                    if file[-3:] == ".py":
                        self.try_load_component(f"{dir_}/{file}")
                    elif "." in file:
                        continue
                    else:
                        to_add.append(f"{dir_}/{file}")

            for item in to_clear:
                dirs_to_do.remove(item)

            for item in to_add:
                dirs_to_do.add(item)

            to_clear = []
            to_add = []

        self.components_loaded = True

    def _load_tilemaps(self) -> None:
        assert self.images_loaded
        assert self.components_loaded

        dirs_to_do: set[str] = set()

        for file in os.listdir(self.game.utilities.DEFAULT_TILEMAP_PATH):
            if "__" in file:
                continue

            if file[-5:] == ".json":
                self.load_tilemap(file)
            elif "." in file:
                continue
            else:
                dirs_to_do.add(file)

        to_clear: list[str] = []
        to_add: list[str] = []
        while dirs_to_do:
            to_clear += dirs_to_do

            for dir_ in dirs_to_do:
                for file in os.listdir(f"{self.game.utilities.DEFAULT_TILEMAP_PATH}/{dir_}"):
                    if "__" in file:
                        continue

                    if file[-5:] == ".json":
                        self.load_tilemap(f"{dir_}/{file}")
                    else:
                        to_add.append(f"{dir_}/{file}")

            for item in to_clear:
                dirs_to_do.remove(item)

            for item in to_add:
                dirs_to_do.add(item)

            to_clear = []
            to_add = []

        self.tilemaps_loaded = True

    def _load_ui_sheets(self) -> None:
        assert self.images_loaded

        dirs_to_do: set[str] = set()

        for file in os.listdir(self.game.utilities.DEFAULT_UI_SHEET_PATH):
            if "__" in file:
                continue

            if file[-5:] == ".json":
                self.load_ui_sheet(file)
            elif "." in file:
                continue
            else:
                dirs_to_do.add(file)

        to_clear: list[str] = []
        to_add: list[str] = []
        while dirs_to_do:
            to_clear += dirs_to_do

            for dir_ in dirs_to_do:
                for file in os.listdir(f"{self.game.utilities.DEFAULT_UI_SHEET_PATH}/{dir_}"):
                    if "__" in file:
                        continue

                    if file[-5:] == ".json":
                        self.load_ui_sheet(f"{dir_}/{file}")
                    else:
                        to_add.append(f"{dir_}/{file}")

            for item in to_clear:
                dirs_to_do.remove(item)

            for item in to_add:
                dirs_to_do.add(item)

            to_clear = []
            to_add = []

        self.ui_sheets_loaded = True
