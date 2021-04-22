import pygame
from pygame.math import Vector2
from typing import Union, Tuple, Optional
import re


def corner(x_pos: Tuple[int, int], x_size: Tuple[int, int]):
    return x_pos[0] - x_size[0] / 2, x_pos[1] - x_size[1] / 2


def center(a: Tuple[int, int], b: Tuple[int, int], offset: Tuple[int, int] = (0, 0)):
    return a[0] / 2 - b[0] / 2 + offset[0], a[1] / 2 - b[1] / 2 + offset[1]


class TextRenderer:

    def __init__(self,
                 scale: int = 1,  # doesn't do anything
                 dimensions: Tuple[int, int] = (1016, 220),  # size of the view window
                 padding: float = 3,  # width of the border
                 inner_padding: float = 4,  # width of the internal border
                 font_family='./Fonts/pixelmix.ttf',
                 font_size=20,
                 text_color=(255, 255, 255),
                 show_cursor=False,
                 antialias=False,
                 start_text='',
                 **kwargs):

        if inner_padding is None:
            inner_padding = padding
        self.padding = padding
        self.inner_padding = inner_padding
        self.total_padding = padding + inner_padding
        self.scale = scale
        self.pos = (10, 426)
        self.text = start_text
        self.text_array = []
        self.color = text_color
        self.show_cursor = show_cursor
        self.antialias = antialias
        self.size = (dimensions[0] - inner_padding * 2,
                     dimensions[1] - inner_padding * 2)

        # create surfaces
        self._image = pygame.Surface((dimensions[0] + padding * 2,
                                      dimensions[1] + padding * 2))
        self.surface = pygame.Surface(self.size)

        # create background and border
        self._image.fill('white')
        inner_pad_surf = pygame.Surface(dimensions)
        inner_pad_surf.fill('black')
        self._image.blit(inner_pad_surf, (padding, padding))

        # create font object
        self.font = pygame.font.Font(font_family, font_size)

        self.text_height = self.font.size('abc')[1]

        # draw the first frame
        self.draw()

    # returns the main surface
    def image(self):
        return self._image

    # called when window is updated
    def drawline(self, offset=(0, 0), radius=3, scale=1):
        scale = self.scale * scale
        self.surface.fill('black')

        textpos = (10, 10 + self.text_height)

        textsurf = self.font.render(self.text, self.antialias, self.color)

        self.surface.blit(textsurf, textpos)
        self._image.blit(self.surface, (self.total_padding, self.total_padding))

    def draw(self, offset=(0, 0), scale=1, end_text: str = ''):
        scale = self.scale * scale
        self.surface.fill('black')

        self.text_array = self.format_text(self.text + (end_text if self.show_cursor else ''))

        pos = lambda x: (10, 10 + x * (self.text_height+6))

        for i, line in enumerate(self.text_array):
            surf = self.font.render(line, self.antialias, self.color)
            self.surface.blit(surf, pos(i))

        self._image.blit(self.surface, (self.total_padding, self.total_padding))

    def format_text(self, text):
        line_start = 0
        arr = []
        reached_text = False  # set to true once it reaches the first line with text

        for i, c in enumerate(text):
            if c in ['\n', '\r']:
                if reached_text or i - line_start > 1:
                    arr.append(text[line_start:i])
                    if not reached_text:
                        reached_text = True
                line_start = i+1
            elif self.font.size(text[line_start:i+1]+'   ')[0] >= self.size[0]:
                arr.append(text[line_start:i+1])
                line_start = i + 1

        if line_start < len(text):
            arr.append(text[line_start:len(text)])

        return arr

    def draw_window(self, offset=(0, 0)):
        self._image.blit(self.surface, (self.total_padding, self.total_padding))

    def clear_text(self):
        self.text = ''

    def add_text(self, text='', newlines=2, replace=False):
        if replace:
            self.text = text
            return
        if newlines > 0:
            self.text += '\n' * newlines
        self.text += text

    def print(self, text: str, draw_func, delay=20):
        self.clear_text()

        for s in text:
            self.add_text(s, 0)
            self.draw()
            draw_func(self.image(), self.pos, delay=delay)

    def print_coroutine(self, i: int, end: int, text: str) -> Optional[int]:
        returnval = None
        if text[i] == '&':
            returnval = int(text[i+1:i+3])
        elif text[i] == '\n':
            returnval = 10

        num = 0
        for s in re.findall('&..|&.|&', text[:i+1]):
            num += len(s)

        text = re.sub('&..', '', text) + ' ' * num

        self.add_text(text[:i+1-num], 0, True)
        self.draw()
        return returnval
        # draw_func(self.image(), self.pos, delay=0)
