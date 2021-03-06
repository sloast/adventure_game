from collections import deque
from typing import List, Optional, Deque
from room import *
from event import *
from pygame.math import Vector2
# from pygame import colordict
from sys import stdout as out
from random import random

sides = {'n': Vector2(0, -1), 'e': Vector2(1, 0), 's': Vector2(0, 1), 'w': Vector2(-1, 0)}
sides_tuples = {'n': (0, -1), 'e': (1, 0), 's': (0, 1), 'w': (-1, 0)}
opposites = {'n': 's', 'e': 'w', 's': 'n', 'w': 'e'}


def printarr(arr):
    for row in arr:
        print(row)


def printmap(arr, word_length=10):
    ln = len(arr)
    print('\n-' + '-' * ((word_length+3) * ln))
    for row in arr:
        out.write('| ')
        for val in row:
            out.write(str((val.name + ' ' * word_length)[:word_length] if val else ' ' * word_length) + ' | ')

        print('\n-' + '-' * ((word_length+3) * ln))


class Map:
    """
    stores all rooms in a 2D list and can return an area of them or generate new rooms
    """

    def __init__(self):
        Room.map_obj = self
        test = False  # use the test layout - will not work with the current version

        if test:
            self.rooms = [Room('Room 1', color='burlywood'), Room('Room 2'), Room('Room 3'), Room('room4r4'), Room('r5'),
                          Empty(),
                          Room('room 7')]
            r = self.rooms
            Room.link_rooms(r[0], r[1], 's')
            Room.link_rooms(r[0], r[2], 'w')
            Room.link_rooms(r[1], r[3], 's')
            Room.link_rooms(r[3], r[4], 'e')
            Room.link_rooms(r[0], r[5], 'n')
            Room.link_rooms(r[4], r[6], 'n')

            self.first_room = r[0]
            self.curr_room = self.first_room
            return

        self.map_radius = 0
        self.side_length = 0
        self.room_chance = 0.6
        self.map: List[List[Optional[Room]]] = []
        self.create_map()

    def create_map(self):
        self.map_radius = 2
        self.side_length = self.map_radius * 2 + 1
        self.map: List[List[Optional[Room]]] = [[None for _ in range(self.side_length)]
                                                for _ in range(self.side_length)]

        self.first_room = Room('Home', 'Like the other rooms, but more brown',
                               coords=(0, 0), color=(130, 80, 50),
                               links={d: True for d in ['n', 's', 'e', 'w']},
                               explored=True)
        self.curr_room = self.first_room
        self.rooms = [self.first_room]

        self.map[2][2] = self.first_room
        # self.map[2][3] = Room('room 2', coords=(1, 0), links={d: True for d in ['n', 's', 'e', 'w']})  # test room

        # Create the rooms surrounding the starting room
        prev_x, prev_y = sides_tuples['w']
        for x, y in sides_tuples.values():

            self.map[y+2][x+2] = \
                Room('Entrance', 'Self-explanatory',  coords=(x, y), color='white',
                     links={d: True for d in ['n', 's', 'e', 'w']},
                     explored=False)

            self.map[y+prev_y+2][x+prev_x+2] = \
                Room('Corner', 'You are now exiting',
                     coords=(x+prev_x, y+prev_y), color='light green',
                     links={d: True for d in ['n', 's', 'e', 'w']},
                     explored=False)

            prev_x, prev_y = x, y

        self.extend_map(3)
        self.generate()
        # self.print_map(explore_all=True)

    def mapper(self):
        pass

    def check_size(self, radius=10, room: Optional[Room] = None):
        if room is None:
            room = self.curr_room

        x, y = room.pos

        if not (self.inrange((x+radius, y+radius)) and self.inrange((x-radius, y-radius))):
            self.extend_map(self.map_radius, True)

    def extend_map(self, radius, add=False):
        side = lambda a: a * 2 + 1

        if add:
            diff = radius
            r = radius + self.map_radius
        else:
            r = radius
            diff = radius - self.map_radius

        side_len = side(r)
        mapper = lambda a, b: (a + diff, b + diff)
        arr: List[List[Optional[Room]]] = [[None for _ in range(side_len)] for _ in range(side_len)]

        for y, row in enumerate(self.map):
            for x, room in enumerate(row):
                if room:
                    new_x, new_y = mapper(x, y)
                    arr[new_y][new_x] = room

        # for row in self.map:
        #    print(row)

        # printmap(arr)

        self.map_radius = r
        self.map = arr

    def add_room(self, new_room, prev_room, direction):
        if prev_room not in self.rooms:
            # return Event('error', 'game', '')
            pass
        Room.link_rooms(prev_room, new_room, direction)
        self.rooms.append(new_room)
        return None

    # deprecated, but could be reused for pathfinding
    def get_visible_area_old(self, distance=3, explore_all=False, room=None):
        if room is None:
            room = self.curr_room

        size = distance * 2 + 1
        start_coords = room.pos

        full_arr = self.get_area(distance, room)

        if explore_all:
            return full_arr

        mapper = lambda a, b: (a - start_coords[0] - distance, b - start_coords[1] - distance)
        local = lambda a, b: (a - distance, b - distance)
        reverselocal = lambda a, b: (a + distance, b + distance)
        in_range = lambda a, b: max(a, b) < size and min(a, b) >= 0

        arr = [[None for _ in range(size)] for _ in range(size)]

        queue: Deque[Tuple[int, int]] = deque([(distance, distance)])
        used = [room]

        arr[distance][distance] = room

        while len(queue) > 0:
            x, y = queue.popleft()
            curr_room: Optional[Room] = full_arr[y][x]
            arr[y][x] = curr_room
            if curr_room is not None and not curr_room.empty() and curr_room.explored():
                for d, (diffx, diffy) in sides_tuples.items():  # Find nearby rooms
                    if self.inrange(local(x+diffx, y+diffy)) and in_range(x+diffx, y+diffy) \
                            and curr_room.has_link(d) \
                            and arr[y+diffy][x+diffx] is None and full_arr[y+diffy][x+diffx] not in used:
                        queue.append((x+diffx, y+diffy))
                        used.append(room)

        return arr

    # improved version of Map.get_visible_area_old() - fixes visibilty issues
    # still very inefficient, but it doesnt matter as the map is relatively small
    def get_visible_area(self, distance=3, explore_all=False, room=None):
        if room is None:
            room = self.curr_room

        size = distance * 2 + 1
        full_arr = self.get_area(distance, room)

        if explore_all:
            return full_arr

        arr: List[List[Optional[Room]]] = [[None for _ in range(size)] for _ in range(size)]

        for y, row in enumerate(full_arr):
            for x, item in enumerate(row):

                if item is None or item.empty():
                    arr[y][x] = Empty()

                elif item.explored():
                    arr[y][x] = item

                else:  # if room is adjacent to an explored room
                    for d in sides:
                        if item.has_link(d) and item.get_linked_room(d).explored():
                            arr[y][x] = item
                            break

        return arr

    # returns all the rooms in the area, even if they are not visible
    def get_area(self, distance=3, room=None):
        if room is None:
            room = self.curr_room

        start_coords = room.pos
        size = distance * 2 + 1
        mapper = lambda a, b: (a + start_coords[0]-distance, b + start_coords[1]-distance)

        arr: List[List[Optional[Room]]] = [[None for _ in range(size)] for _ in range(size)]

        for y, row in enumerate(arr):
            for x, item in enumerate(row):
                if item is None:
                    x2, y2 = mapper(x, y)
                    arr[y][x] = self.get(x2, y2)

        # printmap(arr)
        return arr

    # output the map to the console in a grid
    def print_map(self, distance=3, size=10, explore_all=False, room=None):

        arr = self.get_visible_area(distance, explore_all, room)

        print((('---' + ('-' * size)) * (distance * 2 + 1)) + '-')
        for row in arr:
            s = '| '
            for x in row:
                if x is None:
                    s += (' ' * size) + ' | '
                else:
                    x: Room
                    if x.explored() or explore_all:
                        s += (str(x.name) + (' ' * size))[:size] + ' | '
                    else:
                        s += ('?' * size) + ' | '

            print(s)
            print((('---' + ('-' * size)) * (distance * 2 + 1)) + '-')

    # randomly generate all rooms within a radius of the player
    def generate(self, distance=5, room=None, inplace=True, room_chance=None):
        if room is None:
            room = self.curr_room
        if room_chance is None:
            room_chance = self.room_chance

        self.check_size(distance+2, room)

        start_coords = room.pos
        size = distance * 2 + 1
        mapper = lambda a, b: (a + start_coords[0]-distance, b + start_coords[1]-distance)
        # unused
        # local = lambda a, b: (a-distance, b-distance)
        # localr = lambda a, b: (a + distance, b + distance)

        arr = self.get_visible_area(distance, explore_all=True, room=room)
        # printmap(arr)

        for y, row in enumerate(arr):
            for x, item in enumerate(row):
                if item is None:
                    if random() > room_chance:
                        item = Empty()
                    else:
                        item, new_links = Room.random()

                    arr[y][x] = item
                    if inplace:
                        x2, y2, = mapper(x, y)
                        # print(x, y, x2, y2)
                        if self.get(x2, y2) is None:
                            self.set(x2, y2, item)

        self.update_all_links()

        # Uncomment to print the map to the console
        # printmap(arr)  # prints the local generated array

        # x, y = mapper(0, 0)  # prints the same section from the full map
        # x, y = x+self.map_radius, y+self.map_radius
        # printmap([line[x:x+size] for line in self.map[y:y+size]])

        return arr

    def get(self, x: Union[int, Tuple[int, int]], y: Optional[int] = None, local=True):
        offset = self.map_radius if local else 0
        mapper = lambda a, b: (a + offset, b + offset)
        if y is None:
            x, y = mapper(*x)
        else:
            x, y = mapper(x, y)

        if not self.inrange(x, y, False):
            return None

        return self.map[y][x]

    def inrange(self, x: Union[int, Tuple[int, int]], y: Optional[int] = None, local=True):
        offset = self.map_radius if local else 0
        mapper = lambda a, b: (a + offset, b + offset)
        length = lambda a: a*2 + 1

        if y is None:
            x, y = mapper(*x)
        else:
            x, y = mapper(x, y)

        if x < 0 or x >= length(self.map_radius) or y < 0 or y >= length(self.map_radius):
            return False
        return True

    def set(self, x, y, room: Room, local=True):
        offset = self.map_radius if local else 0
        mapper = lambda a, b: (a + offset, b + offset)
        mapper_b = lambda a, b: (a - offset, b - offset)
        x, y = mapper(x, y)
        self.map[y][x] = room.setpos(mapper_b(x, y))

    def update_all_links(self):
        for row in self.map:
            for room in row:
                if room is not None:
                    room.update_links()
