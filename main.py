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

        logging.basicConfig(format="%(levelname)s:%(name)s:%(message)s", filename="game.log")

    def start(self):
        curses.wrapper(self.GameLoop)

    def generateMap(self, width, height, shape='island', temperature=0.5, wtl=0.5):
        self.map = Map(width, height)
        self.map.generateNewMap((width, height), shape='shape')

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
        for y, row in enumerate(self.map.grid):
            for x, cell in enumerate(row):
                self.draw_hexagon(4*y + 2*(x%2), 2+8*x, str(cell))

    def draw_hexagon(self, y, x, char: str):
        self.map_pad.addstr(y,   x,     "·-----·")
        self.map_pad.addstr(y+1, x-1,  "/       \\")
        self.map_pad.addstr(y+2, x-2, "·    "+char+"    ·")
        self.map_pad.addstr(y+3, x-1,  "\\       /")
        self.map_pad.addstr(y+4, x,     "·-----·")

    def print_map(self, stdscr):

        if self.max_position[0] - self.current_position[0] < self.cols:
            self.map_pad.overwrite(stdscr, self.current_position[1], self.current_position[0], 0, 0, self.rows - 1, self.max_position[0] - self.current_position[0])
            self.map_pad.overwrite(stdscr, self.current_position[1], 0, 0, self.max_position[0] - 3 - self.current_position[0], self.rows - 1, self.cols - 1)
        else:
            self.map_pad.overwrite(stdscr, self.current_position[1], self.current_position[0], 0, 0, self.rows - 1, self.cols - 1)

    def GameLoop(self, stdscr):
        curses.curs_set(False)
        self.map_pad = curses.newpad(3 + 4*self.map.height, 3 + 8*self.map.width)

        self.draw_map()
        self.rows, self.cols = stdscr.getmaxyx()
        self.current_position = [0, 0]

        self.max_position = (3 + 8*self.map.width, 3 + 4*self.map.height)

        while True:
            self.print_map(stdscr)

            stdscr.refresh()

            cmd = stdscr.getch()

            match cmd:
                case curses.KEY_UP:
                    if self.current_position[1] - self.camera_speed >= 0:
                        self.current_position[1] -= self.camera_speed
                case curses.KEY_DOWN:
                    if self.current_position[1] + self.camera_speed <= self.max_position[1]:
                        self.current_position[1] += self.camera_speed
                case curses.KEY_LEFT:
                    if self.current_position[0] - 2*self.camera_speed >= 0:
                        self.current_position[0] -= 2*self.camera_speed
                    else:
                        self.current_position[0] = self.max_position[0] - (2*self.camera_speed - self.current_position[0])
                case curses.KEY_RIGHT:
                    if self.current_position[0] + 2*self.camera_speed < self.max_position[0]:
                        self.current_position[0] += 2*self.camera_speed
                    else:
                        self.current_position[0] = self.current_position[0] + 2*self.camera_speed - self.max_position[0]
                case _:
                    pass
            
            
            
new_game = Game()
new_game.generateMap(100, 60)
new_game.start()