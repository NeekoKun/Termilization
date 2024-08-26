import pygame
import logging
import random
import noise.perlin
import numpy as np
import noise
import math

class Map:
    def __init__(self, width, height) -> None:
        self.width = width
        self.height = height
        self.HOT = 0
        self.WARM = 1
        self.COLD = 2
        self.ICE = 3

    def generate_island_mask(self, center, radius):
        self.mask = []

        for y in range(self.height):
            self.mask.append([])
            for x in range(self.width):
                self.mask[y].append((((y-center[1])**2 + (x-center[0])**2)/radius)**100)
                if self.mask[y][-1] > 1:
                    self.mask[y][-1] = 1
                self.mask[y][-1] = round(1 - self.mask[y][-1], 2)

    def display_matrix(self, matrix: list):
        pygame.display.init()
        scale = 1000 // len(matrix), 1000 // len(matrix[0])
        screen = pygame.display.set_mode((scale[0] * len(matrix), scale[1] * len(matrix[0])))

        for y, row in enumerate(matrix):
            for x, cell in enumerate(row):
                print(cell)
                pygame.draw.rect(screen, (255*cell/3, 255*cell/3, 255*cell/3), pygame.Rect(x*scale[0], y*scale[1], scale[0], scale[1]))
        
        pygame.display.flip()

        while True:
            pass

    def generateNewMap(self, size = None, scale=30, seed=3, radius=10, shape='island', temperature=0):
        if size == None:
            size = (self.width, self.height)

        self.height = size[1]
        self.width = size[0]
        self.elevation_grid = []

        for i in range(size[1]):
            self.elevation_grid.append([])

        ### Generate basic elevation grid ###
        elevation_grid = []

        for i in range(size[1]):
            elevation_grid.append([])
            for j in range(size[0]):
                elevation_grid[i].append(noise.pnoise3(
                    (4*size[0] / math.pi) * math.sin(2*j * math.pi / size[0]) / scale,
                    (4*size[0] / math.pi) * math.cos(2*j * math.pi / size[0]) / scale,
                    (4*i + 2*(j%2)) / scale,
                    base=seed, octaves=3, lacunarity=2, persistence=0.5
                    ))

        mn = min([min(row) for row in elevation_grid])
        elevation_grid = [[i - mn for i in row] for row in elevation_grid]
        mx = max([max(row) for row in elevation_grid])
        elevation_grid = [[i / mx for i in row] for row in elevation_grid]


        # Apply shape mask

        match shape:
            case 'island':
                self.generate_island_mask((len(elevation_grid[0])/2, len(elevation_grid)/2), 70)
            case _:
                self.mask = [[1 for _ in range(self.width)] for _ in range(self.height)]

        elevation_grid = [[cell * self.mask[y][x]  for x, cell in enumerate(row)] for y, row in enumerate(elevation_grid)]

        for y, row in enumerate(elevation_grid):
            for cell in row:
                match cell:
                    case cell if cell < 0.5:
                        self.elevation_grid[y].append(0)
                    case cell if 0.5 <= cell < 0.7:
                        self.elevation_grid[y].append(1)
                    case cell if 0.7 <= cell < 0.9:
                        self.elevation_grid[y].append(2)
                    case cell if 0.9 <= cell:
                        self.elevation_grid[y].append(3)

        ### Generate heat grid ###

        # Plain latitudinal map
        heat_map = [[((abs(i + 0.5*(j%2) - self.height/2)) / (self.height/2)) - temperature for j in range(self.width)] for i in range(self.height)]

        # Perturbate with 3d perlin noise
        turbolence_dim = 3

        turbolence_map = [[
                        noise.pnoise3(
                        (4*self.width / math.pi) * math.sin((2*x) * math.pi / self.width) / scale,
                        (4*self.width / math.pi) * math.cos((2*x) * math.pi / self.width) / scale,
                        (4*y + 2*(x%2)) / scale,
                        base=seed+1) for x, cell in enumerate(row)
                    ] for y, row in enumerate(heat_map)]

        # Normalize and dim turbolence map 

        mn = min([min(row) for row in turbolence_map])
        turbolence_map = [[i - (mn - turbolence_dim) for i in row] for row in turbolence_map]
        mx = max([max(row) for row in turbolence_map])
        turbolence_map = [[i / mx for i in row] for row in turbolence_map]

        # Apply turbolence

        heat_map = [[cell * turbolence_map[y][x] for x, cell in enumerate(row)] for y, row in enumerate(heat_map)]

        # Generate grid from map

        self.heat_grid = []

        hot_threshold = 0.2
        warm_threshold = 0.6
        cold_threshold = 0.8

        for row in heat_map:
            self.heat_grid.append([])
            for cell in row:
                match cell:
                    case cell if cell < hot_threshold:
                        self.heat_grid[-1].append(self.HOT)
                    case cell if hot_threshold <= cell < warm_threshold:
                        self.heat_grid[-1].append(self.WARM)
                    case cell if warm_threshold <= cell < cold_threshold:
                        self.heat_grid[-1].append(self.COLD)
                    case cell if cold_threshold <= cell:
                        self.heat_grid[-1].append(self.ICE)

        self.display_matrix(self.heat_grid)

        ### Generate biome grid ###



        ### Generate Fog of War map ###

        self.fow_grid = [[1 for _ in range(self.width)] for _ in range(self.height)]



    def loadFromRaw(self, raw: list) -> None:
        # Check formatting
        if not len(set(map(len, raw))) <= 1:
            raise TypeError("Raw list not correctly formatted")
        
        self.elevation_grid = []

        for i in range(len(raw[0])):
            self.elevation_grid.append([])

        for column in raw:
            for i, cell in enumerate(column):
                self.elevation_grid[i].append(cell)
        
        # Check for grid values
        pass

        self.height = len(self.elevation_grid)
        self.width = len(self.elevation_grid[0])
    
    def getRaw(self) -> list:
        raw = []

        for i in range(self.width):
            raw.append("")

        for column in self.elevation_grid:
            for i, cell in enumerate(column):
                raw[i] += str(cell)
        
        return raw

if __name__ == "__main__":
    map = Map(100, 100)
    map.generateNewMap()