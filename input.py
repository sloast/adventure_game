"""
This class translates input strings into event.Event objects
"""


from event import *


def add_list(dict_: dict, new: dict):
    for id_, ls in new.items():
        for s in ls:
            dict_[s] = id_


curr_dict = {}


def add(id_: str, *args):
    curr_dict[id_] = id_
    for s in args:
        curr_dict[s] = id_


add('n', 'north', 'up', 'u')
add('e', 'east', 'right', 'r')
add('s', 'south', 'down', 'd')
add('w', 'west', 'left', 'l', 'a')

add('wasd')
add('nesw', 'compass')
add('arrows', 'arrow keys')

add('roominfo', 'room', 'room info')
add('help', 'commands')

inputs = curr_dict
types = {}
curr_dict = types
add('move', 'n', 'e', 's', 'w')
add('input_settings', 'wasd', 'nesw', 'arrows')
add('info', 'roominfo', 'help')


direct_types = ['move', 'help', 'info']

arrows_on = False


class Input:

    @staticmethod
    def get_input(text):
        if text not in inputs:
            return Event('error', 'game', 'invalid_input', {'command': 'none', 'text': text})

        name = inputs[text]
        in_type = types[name]

        if in_type in direct_types:
            return Event(in_type, 'game', name)

        elif in_type == 'input_settings':
            if name == 'wasd':
                inputs['w'] = 'n'
                inputs['d'] = 'e'
                ev = Event('settings', 'game', 'wasd', print='Movement keys changed to WASD')
            elif name == 'nesw':
                inputs['w'] = 'w'
                inputs['d'] = 's'
                ev = Event('settings', 'game', 'nesw', print='Movement keys changed to Compass')
            elif name == 'arrows':
                global arrows_on
                arrows_on = not arrows_on
                ev = Event('settings', 'graphics', 'arrows',
                           print='Arrow keys ' + ('enabled' if arrows_on else 'disabled'))
            else:
                ev = Event('error', 'game', 'input_event_failed',  command=name, text=text)

            return ev

        return Event('error', 'game', 'input_event_failed',  command=name, text=text)

    @staticmethod
    def commandinfo():
        commandlist = []
        string = '\nAvailable commands:\n'
        for command in inputs.values():
            if command not in commandlist:
                commandlist.append(command)
                string += command + ', '
        return string
