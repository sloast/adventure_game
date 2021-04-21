import pygame
from pygame.math import Vector2
from typing import Union, Tuple


def corner(x_pos: Tuple[float, float], x_size: Tuple[float, float]):
    return x_pos[0] - x_size[0] / 2, x_pos[1] - x_size[1] / 2


def center(a: Tuple[float, float], b: Tuple[float, float], offset: Tuple[float, float] = (0, 0)):
    return a[0] / 2 - b[0] / 2 + offset[0], a[1] / 2 - b[1] / 2 + offset[1]


class MapRenderer:
    """
    This class renders everything that appears within the top-left box i.e. game view
    """

    def __init__(self,
                 map_obj,
                 scale: float = 1.25,
                 w_dimensions: Tuple[int, int] = (600, 400),
                 map_dimensions: Tuple[int, int] = (1000, 1000),
                 padding: float = 3,
                 inner_padding: float = 4,
                 **kwargs):
        if inner_padding is None:
            inner_padding = padding
        self.inner_padding = inner_padding
        self.total_padding = padding + inner_padding
        self.scale: float = scale
        self.map = map_obj
        self.window = pygame.Surface((w_dimensions[0] - inner_padding * 2,
                                      w_dimensions[1] - inner_padding * 2))
        self._image = pygame.Surface((w_dimensions[0] + padding * 2,
                                      w_dimensions[1] + padding * 2))
        self._image.fill('white')
        inner_pad_surf = pygame.Surface(w_dimensions)
        inner_pad_surf.fill('black')
        self._image.blit(inner_pad_surf, (padding, padding))
        self.padding = padding
        self.surface = pygame.Surface(map_dimensions)
        p_size: float = 20.0
        p_padding: float = 3.0
        # Rescaling the player caused it to be slightly misshaped
        """
        self.p_size = (p_size * self.scale, p_size * self.scale)
        self.player_surf = pygame.Surface(self.p_size)
        player_center_surf = pygame.Surface(((p_size-p_padding*2) * self.scale, (p_size-p_padding*2) * self.scale))
        self.player_surf.fill('black')
        player_center_surf.fill('red')
        self.player_surf.blit(player_center_surf, (p_padding*self.scale, p_padding*self.scale))
        """
        # Player is not resized according to self.scale
        self.p_size = (p_size, p_size)
        self.player_surf = pygame.Surface(self.p_size)
        player_center_surf = pygame.Surface((p_size - p_padding * 2, p_size - p_padding * 2))
        self.player_surf.fill('black')
        player_center_surf.fill('red')
        self.player_surf.blit(player_center_surf, (p_padding, p_padding))
        self.w_size = (w_dimensions[0] - inner_padding * 2,
                       w_dimensions[1] - inner_padding * 2)
        self.m_size = map_dimensions

        self.pos = (10, 10)
        self.room_size = 100
        self.room_spacing = 30
        self.corridor_width = 25

        self.mm_size = (400, 400)
        self.mm_pos = (300, 100)
        self.minimap = pygame.Surface(self.mm_size)
        self.minimap.set_colorkey((0, 0, 0))
        self.minimap.set_alpha(200)
        self.minimap.fill('black')
        self.mm_scale = 0.1
        self.draw()

    def image(self):
        return self._image

    # called when the map has changed
    def draw(self, offset=(0, 0), radius=5, scale: float = 1,
             explore_all=False, render=True, draw_minimap=True, surf=None, surfsize=None):
        if surf is None:
            surf = self.surface
        if surfsize is None:
            surfsize = self.m_size
        scale = self.scale * scale
        room_size = self.room_size * scale
        corridor_size = self.room_spacing * scale
        room_spacing = room_size + corridor_size

        arr = self.map.get_visible_area(radius, explore_all=explore_all)
        # self.map.print_map(radius, explore_all=False)

        # self.window.fill('black')
        surf.fill('black')

        # self.surface.blit(self.draw_room(arr[3][3]), center(self.m_size, (100, 100)))

        for y, row in enumerate(arr):
            for x, room in enumerate(row):
                if room is not None and not room.empty():
                    x2 = (x - radius) * room_spacing
                    y2 = (y - radius) * room_spacing
                    corridor_dims = (self.room_spacing * scale + 2, self.corridor_width * scale)
                    corridor_dims_b = (0, self.corridor_width * scale)
                    self.draw_links(x2, y2, room, scale, surf, surfsize)

                    surf.blit(self.draw_room(arr[y][x], scale=scale),
                              center(surfsize, (room_size, room_size), (x2, y2)))

        if draw_minimap:
            self.draw(radius=10, scale=self.mm_scale, render=False,
                      draw_minimap=False, surf=self.minimap, surfsize=self.mm_size)

        if render:
            self.draw_window(offset)
        else:
            return surf

    def draw_room(self, room, size=None, scale: float = 1, color: Union[str, Tuple[int, int, int]] = None):
        # scale *= self.scale
        if size is None:
            size = self.room_size * scale

        surf = pygame.Surface((size, size))
        if color:
            surf.fill(color)
        elif room is None:
            surf.fill((50, 0, 0))
        elif not (room.explored() or room == self.map.curr_room):
            surf.fill((100, 100, 100))
        else:
            surf.fill(room.color)

        return surf

    # Draw the corridors between rooms
    def draw_links(self, x, y, room, scale, surf=None, surfsize=None):
        if surf is None:
            surf = self.surface
        if surfsize is None:
            surfsize = self.m_size
        room_size = self.room_size * scale
        corridor_size = self.room_spacing * scale
        room_spacing = room_size + corridor_size
        corridor_dims = (self.room_spacing * scale + 2, self.corridor_width * scale)
        corridor_dims_b = (0, self.corridor_width * scale)

        if room.has_link('e') and not room.get_linked_room('e').empty() \
                and (room.explored() or room.link('e').explored()):
            corr = pygame.Surface(corridor_dims)
            corr.fill('gray')
            surf.blit(corr, center(surfsize, corridor_dims_b, (x + room_size / 2, y)))

        if room.has_link('s') and not room.get_linked_room('s').empty() \
                and (room.explored() or room.link('s').explored()):
            corr = pygame.Surface(corridor_dims[::-1])
            corr.fill('gray')
            surf.blit(corr, center(surfsize, corridor_dims_b[::-1], (x, y + room_size / 2)))

        if room.has_link('w') and not room.get_linked_room('w').empty() \
                and (room.explored() or room.link('w').explored()):
            corr = pygame.Surface(corridor_dims)
            corr.fill('gray')
            surf.blit(corr, center(surfsize, corridor_dims_b, (x - room_size/2 - corridor_size, y)))

        if room.has_link('n') and not room.get_linked_room('n').empty() \
                and (room.explored() or room.link('n').explored()):
            corr = pygame.Surface(corridor_dims[::-1])
            corr.fill('gray')
            surf.blit(corr, center(surfsize, corridor_dims_b[::-1], (x, y - room_size/2 - corridor_size)))

    def draw_window(self, offset=(0, 0)):
        self.window.fill('black')
        self.window.blit(self.surface, center(self.w_size, self.m_size, offset))
        self.window.blit(self.minimap, (self.mm_pos[0] + offset[0] * self.mm_scale,
                                        self.mm_pos[1] + offset[1] * self.mm_scale))
        self.window.blit(self.player_surf, center(self.w_size, self.p_size))
        self._image.blit(self.window, (self.total_padding, self.total_padding))

    def move(self, draw_func, direction, time: int = 30):
        dist = (self.room_size + self.room_spacing) * self.scale
        start = Vector2(0, 0)
        end = {'n': Vector2(0, dist), 'e': Vector2(-dist, 0), 's': Vector2(0, -dist), 'w': Vector2(dist, 0)}[direction]

        for i in range(time):
            self.draw_window(start.lerp(end, (i+1)/time))
            draw_func(self._image, self.pos, 3)
            # pygame.delay(3)

        self.draw()
        draw_func(self._image, self.pos, 0)

    def move_coroutine(self, i: int, end: int, direction: str):
        dist = (self.room_size + self.room_spacing) * self.scale
        start = Vector2(0, 0)
        dest = {'n': Vector2(0, dist), 'e': Vector2(-dist, 0), 's': Vector2(0, -dist), 'w': Vector2(dist, 0)}[direction]

        self.draw_window(start.lerp(dest, (i+1)/end))
        # self.draw(offset=start.lerp(dest, (i+1)/end))

        return
