from typing import Tuple, Union, Optional, Dict
from random import randint, shuffle, random, choice
from pygame import Color, Vector2
from random_words import RandomWords

sides = {'n': (0, -1), 'e': (1, 0), 's': (0, 1), 'w': (-1, 0)}
opposites = {'n': 's', 'e': 'w', 's': 'n', 'w': 'e'}

templates = ['1 of 2', '1\'s 2', 'The 1ian 2',  'The Dungeon of 1', 'Hall of 1', 'The 1 of Mystery']

rw = RandomWords()
debug = True


class Room:
    """
    Represents each of the rooms in the game
    Has many deprecated methods, not removed in case it breaks something
    """

    map_obj = None

    def __init__(self,
                 name: str,
                 description: str = "An ordinary room",
                 coords: Tuple[int, int] = (0, 0),
                 color: Union[str, Tuple[int, int, int]] = None,
                 links: Dict[str, bool] = None,
                 explored: bool = False):
        self.name = name
        self.description = description
        self.pos = coords
        self._explored = explored
        random_color = [randint(0, 200) for _ in range(3)]
        shuffle(random_color)
        self.color = Color(random_color if color is None else color)
        directions = ['n', 's', 'e', 'w']
        # self.links_bool = {'n': False, 'e': False, 's': False, 'w': False}
        self.links_bool = {n: links[n] if n in links else False for n in directions} if links \
            else {n: False for n in directions}

        self.links = {n: self.get_linked_room(n) for n in [d for d in directions if self.has_link(d)]}

        # print(self.links)
        # print(self.links_bool)
        # print()
        # print(self.links_bool)

    def link_room(self, direction: str, room: 'Room' = None):
        if room is None:
            if self.links_bool[direction]:
                return self.links[direction]
            else:
                return None
        else:
            self.links[direction] = room
            self.links_bool[direction] = True

    @staticmethod
    def link_rooms(first, second, direction: str):
        mapper = lambda x: {'n': 's', 's': 'n', 'e': 'w', 'w': 'e'}[x]
        first.link_room(direction, second)
        second.link_room(mapper(direction), first)
        return

    def description(self, description: str = None):
        if description is None:
            return self.description
        else:
            self.description = description

    def empty(self):
        return False

    @staticmethod
    def get_dname(direction_char):
        return {'n': "North", 'e': "East", 's': "South", 'w': "West"}[direction_char]

    # Convert to a string, for printing info
    # Use Room.name to get just the name
    def __str__(self):
        string = ''
        x, y = self.pos
        fastdebug = False  # to print debug info quicker

        if fastdebug and debug:  # Outputs debug info on first two lines
            string += '\n' + self.name + '\n'
            string += 'Pos: (' + str(x) + ', ' + str(y) + ')'
            for d, val in self.links_bool.items():
                string += d.upper() + ': ' + str(1 if val else 0) + ', '

        string += '\n------ ' + self.name + " ------\n" + self.description

        if debug and not fastdebug:  # Debugging information
            string += '\n<Debug>: '
            for d, val in self.links_bool.items():
                string += d.upper() + ': ' + str(1 if val else 0) + ', '
            string += 'Pos: (' + str(x) + ', ' + str(y) + ')'  # Note that north is negative y

        for d in ['n', 's', 'e', 'w']:  # Print nearby rooms
            if d in self.links_bool and self.get_linked_room(d) is not None \
                    and not self.get_linked_room(d).empty():

                l = self.get_linked_room(d)
                string += '\n' + Room.get_dname(d) + ': ' + (l.name if l.explored() else 'Unknown')

        string += '\nLocation: ' + str(-y) + 'N ' + str(x) + 'E'  # print location with compass direction

        return string + ''

    def get_details(self):
        return {'obj': self, 'name': self.name, 'description': self.description, 'links': self.links}

    def get_linked_room_old(self, direction):
        return self.links[direction] if direction in self.links else None

    # This method should be used to get linked rooms
    def get_linked_room(self, direction):
        if self.has_link(direction):
            newpos = (self.pos[0] + sides[direction][0], self.pos[1] + sides[direction][1])
            room = self.map_obj.get(newpos)
            # print(room.name) if room else print('none')
            return Empty() if room is None else room
        else:
            return None

    def get_adj_room(self, direction):
        newpos = (self.pos[0] + sides[direction][0], self.pos[1] + sides[direction][1])
        return self.map_obj.get(newpos)

    # Ensure consistency between adjacent rooms as to whether they are linked or not
    def update_links(self):
        for d, (x, y) in sides.items():
            adj: Room = self.get_adj_room(d)
            if adj and adj.has_link(opposites[d]):
                self.links_bool[d] = True

    def link(self, direction: str, new_room: 'Room' = None):
        return self.link_room(direction, new_room) if new_room else self.get_linked_room(direction)

    def has_link_dict(self, direction):
        return direction in self.links

    # this method should be used for find if a room is linked
    def has_link(self, direction):
        return self.links_bool[direction]

    def explored(self, modify=False, value=True):
        if modify:
            self._explored = value
        return self._explored

    def link_bool(self, direction, value=True):
        self.links_bool[direction] = value

    def setpos(self, x: Union[Tuple[int, int], int], y: Optional[int] = None):
        if y is None:
            self.pos = x
        else:
            self.pos = (x, y)
        return self

    # Create and return a random room
    @staticmethod
    def random(seed=None, pos: Tuple[int, int] = (0, 0)):

        link_chance = 0.6

        links = {'s': random() < link_chance, 'e': random() < link_chance}

        item = Room(Room.random_name(), '<Randomly generated>', coords=pos,
                    links={'s': random() < link_chance, 'e': random() < link_chance})

        return item, links

    # Generates terrible room names
    @staticmethod
    def random_name():
        s = choice(templates)
        for i in range(1, 4):
            if str(i) in s:
                s = s.replace(str(i), rw.random_word().capitalize())
            else:
                break
        return s


class EmptyRoom(Room):

    """
    Represents the absence of a room, as opposed to an area where a room has not yet been generated.
    The Empty() function is used to get a reference to this object
    """

    obj = None

    def __init__(self):
        super().__init__('empty', 'Empty', color='gray')
        EmptyRoom.obj = self

    def __str__(self): return 'Empty'
    def link_room(self, direction: str, room: 'Room' = None): return None
    def description(self, description: str = None): return 'Empty'
    def get_details(self): return 'Empty'
    def explored(self, modify=False, value=True): return False
    def has_link(self, direction): return False
    def empty(self): return True  # Used to tell if a room object is empty
    def get_linked_room(self, direction): return None
    def setpos(self, x, y=None): return self


# Function for getting a reference to the EmptyRoom object
def Empty():
    return EmptyRoom() if EmptyRoom.obj is None else EmptyRoom.obj


# Test code
if __name__ == "__main__":
    r1 = Room('Room 1')
    r2 = Room('Room 2')
    Room.link_rooms(r1, r2, 'e')
    print(r1)
    print()
    print(r2)
