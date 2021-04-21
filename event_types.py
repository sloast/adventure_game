from event import Event


class TextEvent(Event):
    def __init__(self, text, event_type='text', sendto='console', name='TextEvent'):
        super().__init__(event_type, sendto, name)
        self.text = text

    def __str__(self):
        return self.text


class GraphicsEvent(Event):
    def __init__(self, event_type='graphics', sendto='graphics', name='GraphicsEvent'):
        super().__init__(event_type, sendto, name)


class InputEvent(Event):

    def __init__(self, text, name='InputEvent'):
        super().__init__('input', 'game', name)
        self.text = text


class MovementEvent(GraphicsEvent):
    def __init__(self, direction, name='MovementEvent'):
        super().__init__('movement', name)
        self.direction = direction
