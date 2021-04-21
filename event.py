class Event:

    def __init__(
            self,
            event_type: str,  # 'input', 'quit', 'move', 'text', 'error', 'print', 'command'
            sendto: str,
            value: str = 'Event',
            properties: dict = None,
            **kwargs):

        if properties is None:
            properties = {}
        properties.update(kwargs)
        self._type = event_type
        self.name = value
        self._value = value
        self.sendto = sendto
        self.properties = properties

    def __str__(self):
        string = 'Type: ' + self._type + '\nValue: ' + self._value + '\nsendto: ' + self.sendto

        for key, val in self.properties.items():
            string += '\n' + str(key) + ': ' + str(val)

        return string

    def get_value(self, name):
        return self.properties[name]

    def __contains__(self, item):
        return item in self.properties

    def set_value(self, name, new_value):
        old_value = self.properties[name] if name in self.properties else None
        self.properties[name] = new_value
        return old_value

    def __add__(self, other):
        if isinstance(other, list):
            return other.append(self)

        if isinstance(other, Event):
            return [self, other]

    def type(self, new_type=None):
        if new_type is None:
            return self._type
        else:
            self._type = new_type

    def value(self, new_value=None):
        if new_value is None:
            return self._value
        else:
            self._value = new_value
