from scripts.DataStructures.sorted_array import SortedArray
from scripts.GameTypes import SF_key, SortableFunction


class Action:
    # on_need_basis new functions to add in_action and remove in_action
    def __init__(self, game: 'Game', name: str, in_actions: list['Action']=None, order: float=100) -> None:
        if in_actions is None:
            in_actions = []

        self.game: 'Game' = game
        self.name = name
        self.in_actions = in_actions
        self._order = order

        self._my_funkas = [
            (self._order, f"{action.name} -> {self.name}", self.call)  for action in self.in_actions]
        for action, funka in zip(self.in_actions, self._my_funkas):
            action.add(funka)

        self._funkas: SortedArray = SortedArray(SortableFunction, key=SF_key)

    def call(self, args: list|None=None) -> None:
        self.game.utilities.call_functions(self._funkas, args)

    def add(self, funka: SortableFunction) -> None:
        self._funkas.add(funka)

    def remove(self, funka: SortableFunction) -> None:
        self._funkas.remove(funka)

    def detach_from_parents(self) -> None:
        for action, funka in zip(self.in_actions, self._my_funkas):
            if action.has(funka):
                action.remove(funka)

    def __iter__(self):
        for element in self._funkas:
            yield element

    def __getitem__(self, item: int):
        return self._funkas[item]

    def __len__(self) -> int:
        return len(self._funkas)

    def clear(self):
        self._funkas.clear()

    def has(self, element) -> bool:
        return self._funkas.has(element)

    @property
    def reversed(self):
        for element in self._funkas.reversed:
            yield element

    @property
    def as_string(self) -> str:
        if len(self.in_actions) == 0:
            return f"<{self.name}>"

        in_actions = ", ".join([f"<{action.name}>" for action in self.in_actions])
        return f"<{self.name}> <- || {in_actions} ||"

    def __str__(self) -> str:
        return self.as_string

    def __repr__(self) -> str:
        return self.as_string
