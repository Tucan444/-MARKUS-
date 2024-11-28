from scripts.Utilities.component import Component

class TileComponent(Component):
    def __init__(self, name: str, tile: 'Tile'):
        self.name: str = name
        self.tile: 'Tile' = tile

    @property
    def clone(self) -> 'Component':
        return self.load(self.as_json, self.tile)

    @property
    def as_json(self) -> dict:
        return {
            "class_name": self.__name__,
            "name": self.name
        }

    @classmethod
    def load(cls, component_data: dict, tile: 'Tile') -> 'Component':
        return cls(component_data["name"], tile)
