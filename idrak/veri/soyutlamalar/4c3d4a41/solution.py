
from typing import List, Tuple, Iterable, Set

Grid = List[List[int]]


def _clone(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def _find_split_col(grid: Grid) -> int:
    top_row = grid[0]
    for c, v in enumerate(top_row):
        if v != 0:
            return c
    return len(top_row) // 2


def locateLeftWedge(grid: Grid) -> List[Tuple[int, int]]:
    split = _find_split_col(grid)
    return [(r, c) for r, row in enumerate(grid) for c in range(split) if row[c] == 5]


def extractRightBlocks(grid: Grid, wedge_cells: Iterable[Tuple[int, int]]) -> List[int]:
    rows: List[int] = sorted({r for r, _ in wedge_cells})
    return rows


def shiftBlocksUpwards(grid: Grid, rows: Iterable[int]) -> Grid:
    split = _find_split_col(grid)
    h, w = len(grid), len(grid[0])
    out = _clone(grid)
    for src in rows:
        dst = src - 1
        if dst < 0:
            continue
        for c in range(split + 1, w):
            out[dst][c] = grid[src][c]
    return out


def mirrorWedge(shifted: Grid, wedge_cells: Iterable[Tuple[int, int]]) -> Grid:
    split = _find_split_col(shifted)
    h, w = len(shifted), len(shifted[0])
    offset = split + 1
    out = _clone(shifted)
    for r, c in wedge_cells:
        if c + offset < w:
            out[r][c + offset] = 5
    for r in range(h):
        for c in range(split):
            out[r][c] = 0
    return out


def solve_4c3d4a41(grid: Grid) -> Grid:
    wedge_cells = locateLeftWedge(grid)
    blocks = extractRightBlocks(grid, wedge_cells)
    shifted = shiftBlocksUpwards(grid, blocks)
    return mirrorWedge(shifted, wedge_cells)


p = solve_4c3d4a41
