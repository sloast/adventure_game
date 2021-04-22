from event import Event
from room import Room
from player import Player
from map import *
from input import *


class GameController:
    """
    Coordinates the part of the game that manages the logic of the game itself, instead of graphics
    Controls: Player, Room, Map, Input + more when added
    """

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
        self.printqueue = deque([])
        # self.map.print_map(2)

    def update(self):
        queue = self.event_queue
        self.event_queue = []
        return queue

    def event(self, event):
        if event.type() == 'input':
            return self.input_event(event.value())
        elif event.type() == 'keypress':
            self.printnext()
            return []

    def print(self, text, queue=False, multi=False, sendto='all'):
        if multi:
            ev = Event('print', sendto, str(text) + '\npress any key to continue...', text=str(text), multi=True)
        else:
            ev = Event('print', sendto, str(text), text=str(text))
        if queue:
            self.printqueue.append(ev)
        else:
            self.event_queue.append(ev)

    def printnext(self):
        if self.printqueue:
            self.event_queue.append(self.printqueue.popleft())
        else:
            self.print(self.player.room)

    def input_event(self, text, event: Event = None):
        if event is None:
            inp: Event = Input.get_input(text)
        else:
            inp: Event = event
        if inp is None or inp.type() == 'error':
            # error
            self.print('\nCommand not recognized: ' +
                       (('"' + str(inp.get_value('text')) + '"' if inp else 'No input detected') + '\n'),
                       multi=True)
            self.print(self.player.room, queue=True)
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
            elif inp.value() == 'help':
                self.print(Input.help())

        if inp.type() == 'settings':
            ls = [inp]
            if 'print' in inp:
                ls.append(Event('print', 'main', inp.get_value('print')))

            return ls

        return []

    def quit(self):
        pass

