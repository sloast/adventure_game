import pygame
from pygame.math import Vector2
from typing import Union, List, Tuple, Dict, Optional


def corner(x_pos: Tuple[float, float], x_size: Tuple[float, float]):
    return x_pos[0] - x_size[0] / 2, x_pos[1] - x_size[1] / 2


def corner_reverse(x_pos: Tuple[float, float], x_size: Tuple[float, float]):
    return x_pos[0] + x_size[0] / 2, x_pos[1] + x_size[1] / 2


def center(a: Tuple[float, float], b: Tuple[float, float], offset: Tuple[float, float] = (0, 0)):
    return a[0] / 2 - b[0] / 2 + offset[0], a[1] / 2 - b[1] / 2 + offset[1]


class Box:

    def __init__(self,
                 name: str,
                 dimensions: Tuple[float, float] = (400, 400),  # size of the box
                 position: Tuple[float, float] = (0, 0),
                 padding: float = 3,  # width of the border
                 inner_padding: float = 4,  # width of the internal border
                 lines: int = 1,  # lines of text
                 heading: bool = False
                 ):

        self.name = name
        self.lines = lines

        if inner_padding is None:
            inner_padding = padding
        self.padding = padding
        self.inner_padding = inner_padding
        self.total_padding = padding + inner_padding
        self.pos = position
        self.dims = dimensions
        self.size = (dimensions[0] - inner_padding * 2,
                     dimensions[1] - inner_padding * 2)

        self.origin = (0.0, 0.0)
        self.origin_pad = (self.total_padding, self.total_padding)
        self.center_in = (dimensions[0] / 2 - inner_padding, dimensions[1] / 2 - inner_padding)
        self.center = (dimensions[0] / 2, dimensions[1] / 2)
        self.center_pad = (dimensions[0] / 2 + padding, dimensions[1] / 2 + padding)

        # create surfaces
        self._image = pygame.Surface((dimensions[0] + padding * 2, dimensions[1] + padding * 2))
        self.surface = pygame.Surface(self.size)

        # create background and border
        self._image.fill('white')
        inner_pad_surf = pygame.Surface(dimensions)
        inner_pad_surf.fill('black')
        self._image.set_colorkey((0, 0, 0))
        self._image.blit(inner_pad_surf, (padding, padding))

    # returns the main surface
    def image(self):
        return self._image

    def draw(self, surf: pygame.Surface, pos: Tuple[float, float] = (0, 0),
             from_center=False, reset=True) -> pygame.Surface:
        if reset:
            self.surface.fill('black')
        if from_center:
            pos = (pos[0], corner_reverse(pos, self.size)[1])
        self.surface.blit(surf, pos)
        self._image.blit(self.surface, (self.inner_padding, self.inner_padding))
        return self.image()

    def clear(self):
        self.surface.fill('black')

    def draw_window(self, offset=(0, 0)):
        self._image.blit(self.surface, (self.total_padding, self.total_padding))

    def get_end_pos(self):
        return self.pos[0] + self.dims[0] + self.padding, self.pos[1] + self.dims[1] + self.padding

    def get_base(self):
        return self.pos[1] + self.dims[1] + self.padding * 2
