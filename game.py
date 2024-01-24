#!/usr/bin/python3

import pygame
from states import Setup


class Game:
    def __init__(self):
        pygame.init()
        self.done = False
        self.clock = pygame.time.Clock()
        self.bg_color = (0, 0, 100)
        self.fg_color = (255, 255, 255)
        self.hit_color = (255, 0, 0)
        self.tile_size = 40
        self.font = pygame.font.SysFont(None, self.tile_size)
        self.max_fps = 30
        self.state = Setup(self)

    def play(self):
        size = (self.tile_size * 23, self.tile_size * 12)
        self.screen = pygame.display.set_mode(size)
        pygame.display.set_caption("Statki")

        while not self.done:
            self.__handle_events()
            self.state.update()
            self.__render()

    def __handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.done = True
                break
            self.state.handle_event(event)

    def __render(self):
        self.screen.fill(self.bg_color)
        self.state.render()
        pygame.display.flip()
        self.clock.tick(self.max_fps)


if __name__ == "__main__":
    game = Game()
    game.play()
