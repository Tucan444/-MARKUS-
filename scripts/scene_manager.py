import os
import pygame
from scripts.AssetClasses.scene import Scene

class SceneManager:
    EFFECTS: str="___effects___"

    def __init__(self, game: 'Game'):
        self.game: 'Game' = game
        self.scenes: dict[str, Scene] = {}
        self.scenes_ordered: list[Scene] = []

        self._load_scenes()

    def init(self) -> None:
        for scene in self.scenes_ordered:
            if scene.active:
                scene.init()

    def update(self) -> None:
        for scene in self.scenes_ordered:
            if scene.active:
                scene.update()

    def end(self) -> None:
        for scene in self.scenes_ordered:
            if scene.active:
                scene.end()

    @staticmethod
    def get_scene_changer(disable: list[Scene], enable: list[Scene]) -> callable:
        def scene_changer(*_, **__):
            for scene in disable:
                scene.active = False

            for scene in enable:
                scene.active = True

        return scene_changer

    @property
    def as_string(self) -> str:
        return f"number of scenes: {len(self.scenes_ordered)}"

    def __repr__(self):
        return self.as_string

    def __str__(self):
        return self.as_string

    def load_scene(self, path: str) -> bool:
        scene: Scene = self.game.utilities.load_scene(path, self.game)

        if scene.name in self.scenes:
            return False

        self.scenes[scene.name] = scene
        return True

    def _load_scenes(self) -> None:
        dirs_to_do: set[str] = set()

        for file in os.listdir(self.game.utilities.DEFAULT_SCENE_PATH):
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
                inside: list[str] = os.listdir(f"{self.game.utilities.DEFAULT_SCENE_PATH}/{dir_}")
                found_scene: bool = False
                for file in inside:
                    if "__" in file:
                        continue

                    if file[-5:] == ".json":
                        found_scene = True
                        break

                if found_scene:
                    self.load_scene(dir_)
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

        self.scenes_ordered = list(self.scenes.values())
        self.scenes_ordered.sort(key= lambda x: x.order)
