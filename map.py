import numpy as np
import noise
import math

class Map:
    def __init__(self, width=0, height=0) -> None:
        self.width = width
        self.height = height
    
    def island_function(self, x, y, center, radius):
        return (((y-center[1])**2 + (x-center[0])**2)/radius)**200

    def generateNewMap(self, size: list, scale=30, seed=3, radius=10, shape='island'):
        self.grid = []

        for i in range(size[1]):
            self.grid.append([])

        elevation_grid = []
        for i in range(size[1]):
            elevation_grid.append([])
            for j in range(size[0]):
                elevation_grid[i].append(noise.pnoise3(
                    (4*size[0] / math.pi) * math.sin((8*j) * (2 * math.pi) / (8*size[0])) / scale,
                    (4*size[0] / math.pi) * math.cos((8*j) * (2 * math.pi) / (8*size[0])) / scale,
                    (4*i + 2*(j%2)) / scale,
                    base=seed))

        match shape:
            case 'island':
                for y, row in enumerate(elevation_grid):
                    for x, cell in enumerate(row):
                        elevation_grid[y][x] = cell - self.island_function(x, y+0.5*x%2, (len(row)/2, len(elevation_grid)/2), 100)
            case _:
                pass

        for y, row in enumerate(elevation_grid):
            for cell in row:
                match cell:
                    case cell if cell < 0:
                        self.grid[y].append(' ')
                    case cell if 0 <= cell < 0.2:
                        self.grid[y].append(1)
                    case cell if 0.2 <= cell < 0.4:
                        self.grid[y].append(3)
                    case cell if 0.4 <= cell:
                        self.grid[y].append('#')
        
        self.height = len(self.grid)
        self.width = len(self.grid[0])

    def loadFromRaw(self, raw: list) -> None:
        # Check formatting
        if not len(set(map(len, raw))) <= 1:
            raise TypeError("Raw list not correctly formatted")
        
        self.grid = []

        for i in range(len(raw[0])):
            self.grid.append([])

        for column in raw:
            for i, cell in enumerate(column):
                self.grid[i].append(cell)
        
        # Check for grid values
        pass

        self.height = len(self.grid)
        self.width = len(self.grid[0])
    
    def getRaw(self) -> list:
        raw = []

        for i in range(self.width):
            raw.append("")

        for column in self.grid:
            for i, cell in enumerate(column):
                raw[i] += str(cell)
        
        return raw