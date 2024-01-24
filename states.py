import pygame
from pygame.math import Vector2
import random
from board import Board


class Setup:
    def __init__(self, game):
        self.game = game
        self.board = Board(game)
        self.p_ship = None
        self.offset = Vector2(0, 0)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.unicode == '\r':
                self.game.state = Ingame(self.game, self.board)
            elif event.unicode == 'r':
                self.p_ship = None
                self.board = Board(self.game)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = Vector2(event.pos) // self.game.tile_size - (1, 1)
            if self.p_ship is None:
                if (0 <= pos.x < 10 and 0 <= pos.y < 10):
                    for ship in self.board.ships:
                        if pos in ship:
                            if event.button == 1:
                                self.board.ships.remove(ship)
                                self.p_ship = ship
                                self.prev_pos = self.p_ship.start
                                self.prev_rot = self.p_ship.vertical
                                self.offset = pos - ship.start
                            elif event.button == 3:
                                ship.vertical = not ship.vertical
                                if self.board.ship_collides(ship):
                                    ship.vertical = not ship.vertical
                            break
            elif event.button == 3:
                self.p_ship.vertical = not self.p_ship.vertical

        elif (event.type == pygame.MOUSEBUTTONUP and event.button == 1 and
              self.p_ship is not None):
            pos = Vector2(event.pos) // self.game.tile_size - (1, 1)
            self.p_ship.start = pos - self.offset
            if self.board.ship_collides(self.p_ship):
                self.p_ship.start = self.prev_pos
                self.p_ship.vertical = self.prev_rot

            self.board.ships.append(self.p_ship)
            self.p_ship = None
        elif event.type == pygame.MOUSEMOTION and self.p_ship is not None:
            pos = Vector2(event.pos) // self.game.tile_size - (1, 1)
            self.p_ship.start = pos - self.offset

    def update(self):
        pass

    def render(self):
        self.board.render(self.game.screen, (self.game.tile_size,
                          self.game.tile_size), True)
        if self.p_ship:
            self.p_ship.render(
                self.game.screen, self.game.tile_size, (200, 200, 200), 1.5)

        text = self.game.font.render("ENTER - GRAJ", True, self.game.fg_color)
        pos = (self.game.tile_size * 17 - text.get_width() / 2,
               self.game.tile_size * 5.5 - text.get_height() / 2)
        self.game.screen.blit(text, pos)

        text = self.game.font.render("R - LOSUJ", True, self.game.fg_color)
        pos = (self.game.tile_size * 17 - text.get_width() / 2,
               self.game.tile_size * 6.5 - text.get_height() / 2)
        self.game.screen.blit(text, pos)


class Ingame:
    def __init__(self, game, player_board):
        self.game = game
        self.player_board = player_board
        self.cpu_board = Board(game)
        self.last_shot_tick = 0
        self.cpu_targets = []
        self.over = False
        self.win = False
        self.players_turn = True

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.unicode == 'r':
            self.game.state = Setup(self.game)
        if (event.type == pygame.MOUSEBUTTONDOWN and
                self.players_turn and not self.over):
            pos = Vector2(event.pos) // self.game.tile_size - (12, 1)
            if 0 <= pos.x < 10 and 0 <= pos.y < 10:
                result = self.cpu_board.shoot(pos)
                if result == -1:
                    return
                if result == 0:
                    self.players_turn = False
                    self.last_shot_tick = pygame.time.get_ticks()
                for ship in self.cpu_board.ships:
                    if not ship.sunk:
                        return
                self.over = True
                self.win = True

    def update(self):
        if (self.players_turn or self.over
                or pygame.time.get_ticks() - self.last_shot_tick < 300):
            return

        target = Vector2(random.randint(0, 9), random.randint(0, 9))
        if len(self.cpu_targets) == 0:
            for hit in self.player_board.hits:
                ship = self.player_board.ship_at(hit)
                if not ship.sunk:
                    near_hit = False
                    if hit - (0, 1) in self.player_board.hits:
                        near_hit = True
                        self.cpu_targets.append(hit + (0, 1))
                    if hit - (1, 0) in self.player_board.hits:
                        near_hit = True
                        self.cpu_targets.append(hit + (1, 0))
                    if hit + (0, 1) in self.player_board.hits:
                        near_hit = True
                        self.cpu_targets.append(hit - (0, 1))
                    if hit + (1, 0) in self.player_board.hits:
                        near_hit = True
                        self.cpu_targets.append(hit - (1, 0))

                    if not near_hit:
                        self.cpu_targets.append(hit + (0, 1))
                        self.cpu_targets.append(hit + (1, 0))
                        self.cpu_targets.append(hit - (0, 1))
                        self.cpu_targets.append(hit - (1, 0))

        if len(self.cpu_targets) > 0:
            target = self.cpu_targets.pop()

        result = self.player_board.shoot(target)
        if result == -1:
            return
        if result == 0:
            self.players_turn = True
        else:
            self.cpu_targets.clear()

        self.last_shot_tick = pygame.time.get_ticks()
        if result == 2:
            for ship in self.player_board.ships:
                lost = True
                if not ship.sunk:
                    lost = False
                    break
            if lost:
                self.over = True

    def render(self):
        if self.over:
            text = self.game.font.render(
                ("GRACZ" if self.win else "KOMPUTER") + " WYGRYWA, R - RESTART",
                True, self.game.fg_color)
            pos = (self.game.tile_size * 11.5 -
                   text.get_width() / 2, self.game.tile_size * 11.25)
            self.game.screen.blit(text, pos)

        text = self.game.font.render("GRACZ", True, self.game.fg_color)
        pos = (self.game.tile_size * 6 - text.get_width() / 2,
               self.game.tile_size * 0.5 - text.get_height() / 2)
        self.game.screen.blit(text, pos)
        self.player_board.render(
            self.game.screen, (self.game.tile_size, self.game.tile_size), True)

        text = self.game.font.render("KOMPUTER", True, self.game.fg_color)
        pos = (self.game.tile_size * 17 - text.get_width() / 2,
               self.game.tile_size * 0.5 - text.get_height() / 2)
        self.game.screen.blit(text, pos)
        self.cpu_board.render(
            self.game.screen, (self.game.tile_size * 12, self.game.tile_size), False)
