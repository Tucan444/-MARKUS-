from scripts.Utilities.component import Component

class TileComponent(Component):
    def __init__(self, tile: 'Tile'):
        self.tile: 'Tile' = tile

    @property
    def clone(self) -> 'Component':
        return self.load(self.as_json, self.tile)

    @property
    def as_json(self) -> dict:
        return {
            "class_name": self.__class__.__name__
        }

    @classmethod
    def load(cls, component_data: dict, tile: 'Tile') -> 'Component':
        return cls(tile)
