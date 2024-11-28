class Component:
    @property
    def clone(self) -> 'Component':
        return self.load(self.as_json)

    @property
    def as_json(self) -> dict:
        return { "class_name": self.__name__ }

    @classmethod
    def load(cls, component_data: dict) -> 'Component':
        return cls()
