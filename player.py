from event import Event
from room import Room


class Player:
    """
    represents the player's character in the game
    """

    def __init__(self, map_, health=3, items=None):
        self.items = items if items is not None else []
        self.map = map_
        self.room = self.map.first_room
        self.room._explored = True
        self.hp = health

    def move(self, direction):
        new_room: Room = self.room.get_linked_room(direction)
        if new_room is None or new_room.empty():
            ev = Event('error', 'game', 'no_room', p=self, direction=direction, room=self.room)
        else:
            ev = Event('move', 'game', self.room.name + " -> " + new_room.name,
                       p=self, direction=direction, prev_room=self.room,
                       room=new_room, new=new_room.explored())
            self.room = new_room
            self.map.curr_room = new_room
            if not new_room.explored():
                new_room.explored(True)
                self.map.generate()

        return ev
