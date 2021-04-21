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
        self.events: deque = deque([])

        self.gph.update([])

    # Update each frame
    def update(self):
        game_events = []
        if self.events:
            game_events = self.game.event(self.events.popleft())
        game_events.extend(self.game.update())

        self.events.extend(self.gph.update(game_events))

        if game_events is not None:
            for i, e in enumerate(game_events):
                if e.type() == 'print':
                    pass
                    # print(e.value())
                    # self.game_events.pop(i)

    # Begin the game loop
    def run(self):

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
