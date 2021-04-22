from graphics import Graphics
from gamecontroller import GameController
import pygame
from event import Event
from collections import deque


class RunController:
    """
    This class coordinates the entire game and transfers data between different parts
    This file must be run to start the game
    """

    game: GameController = None
    gph: Graphics = None

    # Initialize objects
    def __init__(
            self,
            show_graphics: bool = True):

        self.running: bool = True

        self.game = GameController(self)
        RunController.game = self.game

        self.gph = Graphics(self, self.game.map, self.game.player)
        RunController.gph = self.gph

        self.game_events: list = []
        self.show_graphics: bool = show_graphics
        self.graphics_events: deque = deque([])

    # Update each frame
    def update(self):
        game_events = []
        if self.graphics_events:
            game_events = self.game.event(self.graphics_events.popleft())
        game_events.extend(self.game.update())

        self.graphics_events.extend(self.gph.update(game_events))

        if game_events is not None:
            for e in game_events:
                if e.type() == 'print':
                    pass
                    print(e.value())  # uncomment to print text output also to the console

    # Begin the game loop
    def run(self):
        out = None
        self.gph.intro_start()
        while out is None:
            out = self.gph.intro_update()

        while self.running:
            self.update()

        pygame.quit()

    # Exit the program
    def quit(self):
        self.running = False
        self.game.quit()
        self.gph.quit()


if __name__ == "__main__":
    rcontroller = RunController()
    rcontroller.run()
