import pygame
from pygame.math import Vector2
from typing import Union, List, Tuple, Dict, Optional
from box import *


def corner(x_pos: Tuple[int, int], x_size: Tuple[int, int]):
    return x_pos[0] - x_size[0] / 2, x_pos[1] - x_size[1] / 2


def center(a: Tuple[int, int], b: Tuple[int, int], offset: Tuple[int, int] = (0, 0)):
    return a[0] / 2 - b[0] / 2 + offset[0], a[1] / 2 - b[1] / 2 + offset[1]


class InfoBoxRenderer:
    """
    This class renders the info box to the right of the map
    """

    def __init__(self,
                 map_obj,
                 player_obj,
                 scale: int = 1,  # doesn't do anything
                 dimensions: Tuple[int, int] = (400, 400),  # size of the view window
                 padding: float = 3,  # width of the border
                 inner_padding: float = 4,  # width of the internal border
                 font_family='./Fonts/pixelmix.ttf',
                 font_size=25,
                 text_color=(255, 255, 255),
                 antialias=False,
                 **kwargs):

        self.map = map_obj
        self.player = player_obj

        if inner_padding is None:
            inner_padding = padding
        self.padding = padding
        self.inner_padding = inner_padding
        self.total_padding = padding + inner_padding
        self.scale = scale
        self.pos = (10, 426)
        self.text_array = []
        self.color = text_color
        self.antialias = antialias
        self.dims = dimensions
        self.size = (dimensions[0] - inner_padding * 2,
                     dimensions[1] - inner_padding * 2)

        # create surfaces
        self._image = pygame.Surface((dimensions[0] + padding * 2, dimensions[1] + padding * 2))
        self.surface = pygame.Surface(self.size)

        # create background and border
        self._image.fill('white')
        inner_pad_surf = pygame.Surface(dimensions)
        inner_pad_surf.fill('black')
        self._image.blit(inner_pad_surf, (padding, padding))

        # create font object
        self.font = pygame.font.Font(font_family, font_size)
        self.text_height = self.font.render('abc', self.antialias, self.color).get_height()

        self.box_spacing = 15
        self.box_padding = padding
        self.box_inner_padding = 15
        self.box_width = self.size[0]-2 * self.box_spacing
        self.box_x = self.box_spacing - self.box_padding
        self.box_height = self.text_height + self.box_inner_padding

        self.box_heights: Dict[str, int] = {'health': 1, 'inventory': 4, 'room_name': 1}
        self.data = {'health': 'Health: 3', 'inventory': ['Items:', 'Empty', 'Empty', 'Empty'],
                     'room_name': 'Room 4'}
        self.box_arr = self.create_boxes()

        # draw the first frame
        self.draw()

    def create_boxes(self) -> List[Box]:
        arr = []
        pos = lambda prev, x: (self.box_x, self.box_spacing +
                               (self.inner_padding if x > 0 else 0) + (prev.get_base() if prev else 0))
        size = lambda x: (self.box_width, self.box_inner_padding + self.box_height * x)

        for i, (name, h) in enumerate(self.box_heights.items()):
            arr.append(Box(name, size(h), pos(arr[i-1] if i > 0 else None, i),
                           self.box_padding, self.box_inner_padding, lines=h))

        return arr

    # returns the main surface
    def image(self):
        return self._image

    def draw(self, offset=(0, 0), scale=1):
        scale = self.scale * scale
        self.surface.fill('black')

        # pos = lambda x, h: (10, 10 + x * (h+6))

        self.update()

        for i, (name, text) in enumerate(self.data.items()):
            box = self.box_arr[i]
            if box.lines == 1:
                textsurf = self.font.render(text, self.antialias, self.color)
                # self.surface.blit(box.draw(textsurf, (self.box_inner_padding, -textsurf.get_height()/2),
                #                           from_center=True), box.pos)
                self.surface.blit(box.draw(textsurf), box.pos)
            else:
                self.surface.blit(self.draw_multiline(box, text), box.pos)

        self._image.blit(self.surface, (self.total_padding, self.total_padding))

        return self._image

    def draw_multiline(self, box, text: Union[List[str], str]):
        if isinstance(text, list):
            arr: List[str] = text
        else:
            text: str
            arr: List[str] = text.split('\n', 3)
            arr[-1] = arr[-1].replace('\n', '')

        pos = lambda x, y: (y, self.box_height * x)

        box.clear()

        pad_extra = 10

        for i, line in enumerate(arr):
            box.draw(self.font.render(str(line), self.antialias, self.color),
                     pos(i, (0 if i == 0 else pad_extra)), reset=False)

        return box.image()

    def draw_window(self, offset=(0, 0)):
        self._image.blit(self.surface, (self.total_padding, self.total_padding))

    def update(self):
        self.data['health'] = 'HP: ' + str(self.player.hp)
        a, l, e, = (self.player.items, len(self.player.items), '')
        inv = ['Items: (' + str(l) + '/3)']
        inv.extend(['' + (str(a[i]) if l > i else e) for i in range(3)])
        self.data['inventory'] = inv
        self.data['room_name'] = str(self.map.curr_room.name)
