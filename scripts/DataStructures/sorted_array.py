from scripts.GameTypes import SortableFunction


# optimizable implement with RBT
class SortedArray:
    def __init__(self, type_:type(object), elements: list=None, key=None):
        self.type: type(object) = type_
        self.elements: list[type_] = elements
        if self.elements is None:
            self.elements: list[type_] = []

        self.key: callable = key

    # O(n)
    def add(self, element, sort: bool=True) -> None:
        self.elements.append(element)

        if sort:
            self.sort_elements()

    def sort_elements(self):
        self.elements.sort(key=self.key)

    # O(n)
    def remove(self, element):
        self.elements.remove(element)

    def clear(self):
        self.elements = []

    def has(self, element: bool):
        return element in self.elements

    @property
    def reversed(self):
        for index in range(-1, -1-len(self.elements), -1):
            yield self.elements[index]


    def __str__(self) -> str:
        return str(self.elements)

    def __repr__(self) -> str:
        return str(self.elements)

    def __iter__(self):
        for element in self.elements:
            yield element

    def __getitem__(self, item: int):
        return self.elements[item]

    def __len__(self) -> int:
        return len(self.elements)

if __name__ == '__main__':
    a = SortedArray(float)

    a.add(5.2)
    a.add(4.1)
    a.add(4.2)
    a.add(1.0)
    a.add(5.7)

    print(a)

    for elem in a:
        print(elem)

    for elem in a.reversed:
        print(elem)
        break

    for i in range(len(a)):
        print(a[i])

    print(list(a.reversed))

