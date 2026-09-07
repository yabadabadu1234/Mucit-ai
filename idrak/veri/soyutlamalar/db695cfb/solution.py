
from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Tuple, Set, Iterable

Grid = List[List[int]]
Coord = Tuple[int, int]
DiagonalGroups = Dict[str, Dict[int, List[Coord]]]
SixSeeds = Dict[str, Set[Coord]]


def _clone(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def _fill_nwse_path(grid: Grid, output: Grid, coords: List[Coord], six_seeds: SixSeeds) -> None:
    key = coords[0][0] - coords[0][1]
    rows = [r for r, _ in coords]
    r_min, r_max = min(rows), max(rows)
    width = len(grid[0])
    for r in range(r_min, r_max + 1):
        c = r - key
        if not (0 <= c < width):
            continue
        if grid[r][c] != 6:
            output[r][c] = 1
        if grid[r][c] == 6:
            six_seeds["anti"].add((r, c))


def _fill_nesw_path(grid: Grid, output: Grid, coords: List[Coord], six_seeds: SixSeeds) -> None:
    key = coords[0][0] + coords[0][1]
    rows = [r for r, _ in coords]
    r_min, r_max = min(rows), max(rows)
    width = len(grid[0])
    for r in range(r_min, r_max + 1):
        c = key - r
        if not (0 <= c < width):
            continue
        if grid[r][c] != 6:
            output[r][c] = 1
        if grid[r][c] == 6:
            six_seeds["main"].add((r, c))


def _fill_diag(output: Grid, seed: Coord, orientation: str) -> None:
    height, width = len(output), len(output[0])
    r0, c0 = seed
    if orientation == "anti":
        diag_sum = r0 + c0
        for r in range(height):
            c = diag_sum - r
            if 0 <= c < width:
                if output[r][c] == 1 and (r, c) != seed:
                    continue
                output[r][c] = 6
    else:
        diff = r0 - c0
        for r in range(height):
            c = r - diff
            if 0 <= c < width:
                if output[r][c] == 1 and (r, c) != seed:
                    continue
                output[r][c] = 6


def groupAnchorsByDiagonal(grid: Grid) -> DiagonalGroups:
    height = len(grid)
    width = len(grid[0]) if grid else 0
    if height == 0 or width == 0:
        return {"main": {}, "anti": {}}

    ones: List[Coord] = [(r, c) for r in range(height) for c in range(width) if grid[r][c] == 1]
    groups_main: Dict[int, List[Coord]] = defaultdict(list)
    groups_anti: Dict[int, List[Coord]] = defaultdict(list)
    for r, c in ones:
        groups_main[r - c].append((r, c))
        groups_anti[r + c].append((r, c))
    return {"main": dict(groups_main), "anti": dict(groups_anti)}


def paintOnePaths(grid: Grid, diagonal_groups: DiagonalGroups) -> Tuple[Grid, SixSeeds]:
    painted = _clone(grid)
    six_seeds: SixSeeds = {"anti": set(), "main": set()}

    for coords in diagonal_groups.get("main", {}).values():
        if len(coords) >= 2:
            _fill_nwse_path(grid, painted, coords, six_seeds)

    for coords in diagonal_groups.get("anti", {}).values():
        if len(coords) >= 2:
            _fill_nesw_path(grid, painted, coords, six_seeds)

    return painted, six_seeds


def extendSixDiagonals(painted: Grid, six_seeds: SixSeeds) -> Grid:
    extended = _clone(painted)
    for seed in six_seeds.get("anti", set()):
        _fill_diag(extended, seed, "anti")
    for seed in six_seeds.get("main", set()):
        _fill_diag(extended, seed, "main")
    return extended


def finaliseGrid(original: Grid, extended: Grid) -> Grid:
    return extended


def solve_db695cfb(grid: Grid) -> Grid:
    diagonal_groups = groupAnchorsByDiagonal(grid)
    painted, six_seeds = paintOnePaths(grid, diagonal_groups)
    extended = extendSixDiagonals(painted, six_seeds)
    return finaliseGrid(grid, extended)


p = solve_db695cfb
