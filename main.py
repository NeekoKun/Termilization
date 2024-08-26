import logging
from map import Map
import sys
import curses
import json

class Game:
    def __init__(self) -> None:
        with open("settings.json", 'r') as file:
            self.settings = json.load(file)

        self.camera_speed = self.settings["camera speed"]

        self.DESERT = 9
        self.PLAIN = 10
        self.TUNDRA = 11
        self.SNOW = 12
        self.DESERT_HILL = self.DESERT + 100
        self.PLAIN_HILL = self.PLAIN + 100
        self.TUNDRA_HILL = self.TUNDRA + 100
        self.SNOW_HILL = self.SNOW + 100
        self.MOUNTINE = 13
        self.SEA = 14

        logging.basicConfig(format="%(levelname)s:%(name)s:%(message)s", filename="game.log")

    def init_colors(self):
        curses.start_color()

        curses.init_color(self.DESERT, 969, 863, 725)
        curses.init_color(self.DESERT_HILL, 871, 675, 502)
        curses.init_color(self.PLAIN, 506, 635, 388)
        curses.init_color(self.PLAIN_HILL, 212, 369, 196)
        curses.init_color(self.TUNDRA, 251, 325, 298)
        curses.init_color(self.TUNDRA_HILL, 412, 459, 396)
        curses.init_color(self.SNOW, 957, 957, 949)
        curses.init_color(self.SNOW_HILL, 910, 910, 910)
        curses.init_color(self.MOUNTINE, 208, 216, 294)
        curses.init_color(self.SEA, 12, 204, 431)
        
    def start(self):
        curses.wrapper(self.GameLoop)

    def generateMap(self, width, height, shape='is', temperature=0):
        self.map = Map(width, height)
        self.map.generateNewMap(shape=shape, temperature=temperature)

    def save(self):
        raw = self.map.getRaw()

        with open(self.settings["saveFile"], 'w') as save:
            save.writelines(f"{row}\n" for row in raw)

    def load(self):
        with open(self.settings["saveFile"], 'r') as save:
            grid = list(map(str.strip, save.readlines()))
        
        self.map = Map()
        self.map.loadFromRaw(grid)

    def draw_map(self):
        for y, row in enumerate(self.map.elevation_grid):
            for x, cell in enumerate(row):
                properties = {}

                properties["elevation"] = cell
                properties["heat"] = self.map.heat_grid[y][x]

                self.draw_hexagon(4*y + 2*(x%2), 2+8*x, properties)

    def draw_hexagon(self, y, x, properties: dict):
        # Draw frame
        # TODO: modify frame color in function of country borders

        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)

        self.map_pad.addstr(y,   x,     "·-----·",   curses.color_pair(1))
        self.map_pad.addstr(y+1, x-1,  "/       \\", curses.color_pair(1))
        self.map_pad.addstr(y+2, x-2, "·         ·", curses.color_pair(1))
        self.map_pad.addstr(y+3, x-1,  "\\       /", curses.color_pair(1))
        self.map_pad.addstr(y+4, x,     "·-----·",   curses.color_pair(1))

        # Draw content

        match properties["elevation"]:
            case 0:
                color = self.SEA
            case 1:
                color = properties["heat"] + 9
            case 2:
                color = properties["heat"] + 109
            case 3:
                color = self.MOUNTINE

        logging.warning(color)

        curses.init_pair(color, curses.COLOR_WHITE, color)

        logging.warning(curses.color_pair(2))

        self.map_pad.addstr(y+1, x,    "       ",  curses.color_pair(color))
        self.map_pad.addstr(y+2, x-1, "    "+str(properties["heat"])+"    ", curses.color_pair(color))
        self.map_pad.addstr(y+3, x,    "       ",  curses.color_pair(color))
                
    def print_map(self, stdscr):
        self.map_pad.refresh(self.current_position[1], self.current_position[0], 0, 0, self.rows - 1, self.cols - 1)

    def GameLoop(self, stdscr):
        curses.curs_set(False)

        self.init_colors()

        self.map_pad = curses.newpad(3 + 4*self.map.height, 3 + 8*self.map.width)

        self.draw_map()
        self.rows, self.cols = stdscr.getmaxyx()
        self.current_position = [0, 0]

        self.max_position = ((3 + 8*self.map.width) - (self.cols), (3 + 4*self.map.height) - (self.rows))

        while True:
            stdscr.refresh()
            self.print_map(stdscr)


            cmd = stdscr.getch()

            match cmd:
                case curses.KEY_UP:
                    if self.current_position[1] - self.camera_speed >= 0:
                        self.current_position[1] -= self.camera_speed
                    else:
                        self.current_position[1] = 0
                case curses.KEY_DOWN:
                    if self.current_position[1] + self.camera_speed <= self.max_position[1]:
                        self.current_position[1] += self.camera_speed
                    else:
                        self.current_position[1] = self.max_position[1]
                case curses.KEY_LEFT:
                    if self.current_position[0] - 2*self.camera_speed >= 0:
                        self.current_position[0] -= 2*self.camera_speed
                    else:
                        self.current_position[0] = 0
                case curses.KEY_RIGHT:
                    if self.current_position[0] + 2*self.camera_speed < self.max_position[0]:
                        self.current_position[0] += 2*self.camera_speed
                    else:
                        self.current_position[0] = self.max_position[0]
                case _:
                    pass


new_game = Game()
new_game.generateMap(100, 100, temperature=0.2)
new_game.start()