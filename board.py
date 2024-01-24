import pygame
from pygame.math import Vector2
import random


class Ship:
    def __init__(self, start, length, vertical):
        self.start = start
        self.length = length
        self.vertical = vertical
        self.sunk = False

    @property
    def end(self):
        length = self.length - 1
        if self.vertical:
            return self.start + (0, length)
        else:
            return self.start + (length, 0)

    @property
    def tiles(self):
        tiles = [self.start]
        if self.vertical:
            for i in range(self.length):
                tiles.append(self.start + (0, i))
        else:
            for i in range(self.length):
                tiles.append(self.start + (i, 0))
        return tiles

    @property
    def tiles_around(self):
        tiles = [self.start]
        if self.vertical:
            for i in range(self.length + 2):
                tiles.append(self.start + (0, i - 1))
                tiles.append(self.start + (1, i - 1))
                tiles.append(self.start + (-1, i - 1))
        else:
            for i in range(self.length + 2):
                tiles.append(self.start + (i - 1, 0))
                tiles.append(self.start + (i - 1, 1))
                tiles.append(self.start + (i - 1, -1))
        return tiles

    def render(self, surface, tile_size, color, offset=0.5):
        pygame.draw.line(surface, color,
                         ((self.start + (offset, offset)) * tile_size),
                         ((self.end + (offset, offset)) * tile_size), 10)

    def __contains__(self, tile):
        return tile in self.tiles


class Board:
    def __init__(self, game, ships=None):
        self.game = game
        self.surface = pygame.Surface(
            (self.game.tile_size * 10, self.game.tile_size * 10))
        if ships is None:
            self.__place_ships_at_random()
        else:
            self.ships = ships
        self.shots = []
        self.hits = []

    def __place_ships_at_random(self):
        remaining_ships = [5, 4, 3, 3, 2, 2]
        self.ships = []
        while len(remaining_ships):
            start = Vector2(random.randint(0, 9), random.randint(0, 9))
            ship_length = remaining_ships[0]
            vertical = random.randint(0, 1)
            new_ship = Ship(start, ship_length, vertical)

            if self.ship_collides(new_ship):
                continue

            self.ships.append(new_ship)
            remaining_ships.pop(0)

    def ship_collides(self, ship):
        if (ship.end.x > 9 or ship.end.y > 9 or ship.start.x < 0 or
                ship.start.y < 0):
            return True

        for other in self.ships:
            if other == ship:
                continue
            for tile in ship.tiles_around:
                if tile in other.tiles:
                    return True

        return False

    def ship_at(self, pos):
        for ship in self.ships:
            if pos in ship:
                return ship
        return None

    def shoot(self, pos):
        if (pos in self.shots or not (0 <= pos[0] <= 9)
                or not (0 <= pos[1] <= 9)):
            return -1
        else:
            self.shots.append(pos)
            ship = self.ship_at(pos)
            if ship is not None:
                self.hits.append(pos)
                for tile in ship.tiles:
                    if tile not in self.hits:
                        return 1
                ship.sunk = True
                for tile in ship.tiles_around:
                    if tile not in self.shots:
                        self.shots.append(tile)
                return 2
            return 0

    def render(self, dest, offset, render_ships):
        self.surface.fill(self.game.bg_color)
        pygame.draw.lines(self.surface, self.game.fg_color, True,
                          [(0, 0), (self.surface.get_width() - 1, 0),
                           (self.surface.get_width() - 1,
                            self.surface.get_height() - 1),
                           (0, self.surface.get_height() - 1)], 3)
        for i in range(1, 10):
            pygame.draw.line(self.surface, self.game.fg_color,
                             (i * self.game.tile_size, 0),
                             (i * self.game.tile_size, self.surface.get_height()))
            pygame.draw.line(self.surface, self.game.fg_color,
                             (0, i * self.game.tile_size),
                             (self.surface.get_width(), i * self.game.tile_size))
        for ship in self.ships:
            if (render_ships or ship.sunk):
                color = self.game.fg_color if not ship.sunk else self.game.hit_color
                ship.render(self.surface, self.game.tile_size, color)
        for shot in self.shots:
            color = self.game.fg_color if shot not in self.hits else self.game.hit_color
            pygame.draw.line(self.surface, color,
                             (shot[0] * self.game.tile_size,
                              shot[1] * self.game.tile_size),
                             ((shot[0] + 1) * self.game.tile_size,
                              (shot[1] + 1) * self.game.tile_size), 5)
            pygame.draw.line(self.surface, color,
                             ((shot[0] + 1) * self.game.tile_size,
                              shot[1] * self.game.tile_size),
                             (shot[0] * self.game.tile_size,
                              (shot[1] + 1) * self.game.tile_size), 5)

        dest.blit(self.surface, offset)
