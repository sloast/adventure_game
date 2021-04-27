

class Item:

    def __init__(self,
                 name: str,
                 desc: str = 'Item',
                 effects: dict = None):
        self.name = name
        self.description = desc
        self.effects = {} if effects is None else effects

    def __str__(self):
        return self.name
