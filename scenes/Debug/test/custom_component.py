from scripts.Utilities.component import Component


class CustomComponent(Component):
    def __init__(self):
        super().__init__()

class CustomComponent2(Component):
    def __init__(self):
        super().__init__()

class CustomComponent3(CustomComponent2):
    def __init__(self):
        super().__init__()
