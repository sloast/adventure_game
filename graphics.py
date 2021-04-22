from collections import deque

import pygame
from textinput import TextInput
from pygame.locals import *
from event import Event
from map_renderer import *
from text_renderer import *
from infobox_renderer import *
from coroutine import *


class Graphics:
    """
    Class to coordinate everything to do with graphics and the view window
    """

    def __init__(
            self,
            run_controller,
            map_obj,
            player_obj,
            screen_dimensions=(1042, 800),
            **kwargs):

        from main import RunController
        self.rcont: RunController = run_controller

        pygame.init()
        pygame.font.init()
        pygame.display.set_caption('an interesting title')
        pygame.key.set_repeat()

        self.map = MapRenderer(map_obj)
        self.output = TextRenderer()
        self.infobox = InfoBoxRenderer(map_obj, player_obj)

        self.SCREEN_DIMENSIONS = screen_dimensions
        self.screen = pygame.display.set_mode(self.SCREEN_DIMENSIONS)

        self.text_box = pygame.Surface((368, 46))
        self.text_box.fill('white')
        text_box_inner = pygame.Surface((362, 40))
        text_box_inner.fill('black')
        self.text_box.blit(text_box_inner, (3, 3))

        self.textinput = TextInput(font_family='./Fonts/pixelmix.ttf', font_size=25, text_color=(255, 255, 255),
                                   cursor_color=(255, 255, 255), max_string_length=16, front_text="> ",
                                   antialias=False, horizontal_cursor=True)

        self.text_out_params = {'font_family': './Fonts/pixelmix.ttf', 'font_size': 25, 'text_color': (100, 100, 100),
                                'max_string_length': 18, 'front_text': "",
                                'antialias': False, 'show_cursor': False}

        self.textoutput1 = TextInput(**self.text_out_params)
        self.text_out_params['text_color'] = (50, 50, 50)
        self.textoutput2 = TextInput(**self.text_out_params)

        self.arrowspressed = {K_UP: False, K_DOWN: False, K_LEFT: False, K_RIGHT: False}
        self.arrowspressed = {d: False for d in [K_UP, K_DOWN, K_LEFT, K_RIGHT]}

        self.clock = pygame.time.Clock()
        self.queue = deque([])
        self.coroutines = deque([])
        self.arrows_enabled = True
        self.await_input = False

    def intro_start(self):
        intro_text = 'initializing&20.&20.&20.&20\n\nwelcome to adventure_game.py!\n' \
                     'you can type commands to move or carry out other actions.\n' \
                     'type \'help\' for a full list of available commands.\n' \
                     '\npress any key to continue...'
        Coroutine(self.output.print_coroutine, len(intro_text), delay=1, singular_type=TextOutput,
                  end_func=Coroutine.invoke(self.output.draw, 4), text=intro_text)

    def intro_update(self):

        output = None

        events = pygame.event.get()

        if self.textinput.update(events) and Coroutine.input():
            input_text = self.textinput.get_text().lower()
            if len(input_text) > 0:
                output = (Event('input', 'game', input_text,
                                text=input_text))
                self.textinput.clear_text()
                print('> ' + input_text)
            self.prev_input(input_text)

        for event in events:
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                self.rcont.quit()
                return Event('quit', 'all', 'graphics_quit')
            elif event.type == KEYDOWN:
                return Event('start', 'main', 'game_start')

        Coroutine.update()
        self.screen.fill((0, 0, 0))

        self.screen.blit(self.text_box, (10, self.SCREEN_DIMENSIONS[1] - 56))
        self.screen.blit(self.textoutput2.get_surface(), (20, self.SCREEN_DIMENSIONS[1] - 130))
        self.screen.blit(self.textoutput1.get_surface(), (20, self.SCREEN_DIMENSIONS[1] - 90))
        self.screen.blit(self.textinput.get_surface(), (20, self.SCREEN_DIMENSIONS[1] - 47))

        # self.screen.blit(self.map.image(), (10, 10))
        # self.screen.blit(self.infobox.draw(), (626, 10))
        self.screen.blit(self.output.image(), (10, 426))

        pygame.display.flip()

        self.clock.tick(40)

        return output

    def update(self, game_events=None):
        if game_events is None:
            game_events = []
        self.queue.extend(deque(game_events))

        output = []
        events = pygame.event.get()

        if self.textinput.update([] if self.await_input or not Coroutine.input() else events):
            input_text = self.textinput.get_text().lower()
            if len(input_text) > 0:
                output.append(Event('input', 'game', input_text,
                                    text=input_text))
                self.textinput.clear_text()
                print('> ' + input_text)
            self.prev_input(input_text)

        # print([str(event.type) + '-' + str(event.key) for event in events])
        arrow_pressed = False
        for event in events:
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                self.rcont.quit()
                return [Event('quit', 'all', 'graphics_quit')]

            # broken
            if not self.await_input and not arrow_pressed and self.arrows_enabled \
                    and Coroutine.input() and event.type == KEYDOWN\
                    and pygame.key.get_pressed()[event.key]:
                key_vals = {K_UP: 'north', K_DOWN: 'south', K_LEFT: 'west', K_RIGHT: 'east'}
                if event.key in key_vals:
                    ev = Event('input', 'game', key_vals[event.key],
                               text=key_vals[event.key])

                    self.queue.extend(self.rcont.game.event(ev))
                    # output.append(ev)

                    self.prev_input(key_vals[event.key])
                    self.textinput.clear_text()
                    arrow_pressed = True
                    print(key_vals[event.key])
                # print(pygame.key.get_pressed()[event.key])

            elif self.await_input and event.type == KEYDOWN:
                self.await_input = False
                output.append(Event('keypress', 'game', 'continue'))

        while len(self.queue) > 0:
            event = self.queue.popleft()
            if event.type() == 'move':
                # self.map.move(self.draw_surf, event.get_value('direction'))
                Coroutine(self.map.move_coroutine, 40, delay=0, singular_type=MapAction, end_func=self.map.draw,
                          forbid_input=True, direction=event.get_value('direction'))

            if event.type() == 'settings':
                if event.value() == 'arrows':
                    self.arrows_enabled = not self.arrows_enabled

            if event.type() == 'print':
                # if event.sendto in ['all', 'graphics']:
                # self.output.print(str(event.value()), self.draw_surf)
                text = str(event.value()).strip('\n')
                Coroutine(self.output.print_coroutine, len(text), delay=1, singular_type=TextOutput,
                          end_func=Coroutine.invoke(self.output.draw, 4), text=text)
                if 'multi' in event:
                    self.await_input = True

        Coroutine.update()
        self.screen.fill((0, 0, 0))

        self.screen.blit(self.text_box, (10, self.SCREEN_DIMENSIONS[1] - 56))
        self.screen.blit(self.textoutput2.get_surface(), (20, self.SCREEN_DIMENSIONS[1] - 130))
        self.screen.blit(self.textoutput1.get_surface(), (20, self.SCREEN_DIMENSIONS[1] - 90))
        self.screen.blit(self.textinput.get_surface(), (20, self.SCREEN_DIMENSIONS[1] - 47))

        self.screen.blit(self.map.image(), (10, 10))
        self.screen.blit(self.infobox.draw(), (626, 10))
        self.screen.blit(self.output.image(), (10, 426))

        pygame.display.flip()

        self.clock.tick(40)

        return output

    def draw_surf(self, surf, pos=(0, 0), delay=0):
        self.screen.blit(surf, pos)
        pygame.display.flip()
        pygame.time.delay(delay)

    def prev_input(self, text=''):
        self.textoutput2.set_text(self.textoutput1.get_text())
        self.textoutput1.set_text('> ' + text)
        self.textoutput1.update([])
        self.textoutput2.update([])

    def quit(self):
        pass
