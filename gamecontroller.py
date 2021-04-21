from event import Event
from room import Room
from player import Player
from map import *
from input import *


class GameController:

    player: Player = None
    map: Map = None

    def __init__(self, rcontroller):

        from main import RunController
        self.rcont: RunController = rcontroller
        self.event_queue = []
        self.map = Map()
        GameController.map = self.map
        self.player = Player(self.map)
        GameController.player = self.player
        self.print(self.player.room)
        self.map.print_map(2)

    def update(self):
        queue = self.event_queue
        self.event_queue = []
        return queue

    def event(self, event):
        if event.type() == 'input':
            return self.input_event(event.value())

    def print(self, text, sendto='all'):
        self.event_queue.append(Event('print', sendto, text, text=text))

    def input_event(self, text, event=None):
        inp: Event = Input.get_input(text)
        if inp is None or inp.type() == 'error':
            # error
            self.print('\n-----ERROR-----\ninvalid input:' + (('\n' + str(inp)) if inp else 'No input detected'))
            self.print(self.player.room)
            return []

        if inp.type() == 'move':
            move_ev = self.player.move(inp.value())
            s = ''
            if move_ev.type() == 'error':
                s = 'There is no room in that direction!\n'
            self.print(s + str(self.player.room))
            # self.map.print_map(2)
            return [move_ev]

        if inp.type() == 'info':
            if inp.value() == 'roominfo':
                self.print(self.player.room)
                return []

        if inp.type() == 'settings':
            ls = [inp]
            if 'print' in inp:
                ls.append(Event('print', 'main', inp.get_value('print')))

            return ls

        return []

    def quit(self):
        pass

