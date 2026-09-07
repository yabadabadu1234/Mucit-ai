
from typing import List

Grid = List[List[int]]


def cloneGrid(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def solve_da515329(grid: Grid) -> Grid:
    return cloneGrid(grid)


p = solve_da515329
