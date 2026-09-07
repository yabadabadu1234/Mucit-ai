
from __future__ import annotations

from collections import deque
from typing import Iterable, List, Sequence, Set, Tuple, TypedDict

Grid = List[List[int]]
Point = Tuple[int, int]


class Motif(TypedDict):
    coords: List[Point]
    colors: Set[int]
    bbox: Tuple[int, int, int, int]
    threes: List[Tuple[Point, List[Tuple[int, int]]]]
    fours: List[Tuple[Point, List[Tuple[int, int]]]]


class GuideGraph(TypedDict):
    shape: Tuple[int, int]
    candidates: Set[Point]
    sentinel: Set[Point]


def _component_scan(grid: Grid) -> List[Motif]:

    h, w = len(grid), len(grid[0])
    visited = [[False] * w for _ in range(h)]
    components: List[Motif] = []

    for r in range(h):
        for c in range(w):
            if grid[r][c] == 8 or visited[r][c]:
                continue

            stack = [(r, c)]
            visited[r][c] = True
            coords: List[Point] = []
            colors: Set[int] = set()

            while stack:
                x, y = stack.pop()
                coords.append((x, y))
                colors.add(grid[x][y])

                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < h and 0 <= ny < w and not visited[nx][ny] and grid[nx][ny] != 8:
                        visited[nx][ny] = True
                        stack.append((nx, ny))

            rows = [x for x, _ in coords]
            cols = [y for _, y in coords]
            min_r, min_c, max_r, max_c = min(rows), min(cols), max(rows), max(cols)

            threes: List[Tuple[Point, List[Tuple[int, int]]]] = []
            fours: List[Tuple[Point, List[Tuple[int, int]]]] = []
            for x, y in coords:
                directions = []
                if x == min_r:
                    directions.append((-1, 0))
                if x == max_r:
                    directions.append((1, 0))
                if y == min_c:
                    directions.append((0, -1))
                if y == max_c:
                    directions.append((0, 1))

                value = grid[x][y]
                if value == 3:
                    threes.append(((x, y), directions))
                elif value == 4:
                    fours.append(((x, y), directions))

            components.append(
                Motif(
                    coords=coords,
                    colors=colors,
                    bbox=(min_r, min_c, max_r, max_c),
                    threes=threes,
                    fours=fours,
                )
            )

    return components


def _extend_ray(grid: Grid, origin: Point, direction: Tuple[int, int]) -> List[Point]:

    h, w = len(grid), len(grid[0])
    dr, dc = direction
    r, c = origin[0] + dr, origin[1] + dc
    ray: List[Point] = []

    while 0 <= r < h and 0 <= c < w and grid[r][c] == 8:
        ray.append((r, c))
        r += dr
        c += dc

    return ray


def extractMotifs(grid: Grid) -> List[Motif]:
    return _component_scan(grid)


def filterByGuideCount(motifs: Sequence[Motif]) -> List[Motif]:
    return [m for m in motifs if len(m["threes"]) >= 2]


def _find_sentinel(motifs: Iterable[Motif]) -> Motif:
    return next(m for m in motifs if 2 in m["colors"])


def buildGuideGraph(grid: Grid, filtered: Sequence[Motif]) -> GuideGraph:
    motifs = _component_scan(grid)
    sentinel = _find_sentinel(motifs)

    candidates: Set[Point] = set(sentinel["coords"])

    for (cell, directions) in sentinel["fours"]:
        direction = next((d for d in directions if d == (-1, 0)), None)
        if direction is None and directions:
            direction = directions[0]
        if direction:
            candidates.update(_extend_ray(grid, cell, direction))

    for comp in filtered:
        candidates.update(comp["coords"])
        for (cell, directions) in comp["threes"]:
            if not directions:
                continue
            candidates.update(_extend_ray(grid, cell, directions[0]))

    h, w = len(grid), len(grid[0])
    return GuideGraph(shape=(h, w), candidates=candidates, sentinel=set(sentinel["coords"]))


def propagateScaffold(graph: GuideGraph) -> Grid:
    h, w = graph["shape"]
    candidates = graph["candidates"]
    start = graph["sentinel"]

    queue = deque(start)
    reachable: Set[Point] = set(start)

    while queue:
        r, c = queue.popleft()
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            nxt = (nr, nc)
            if nxt in candidates and nxt not in reachable:
                reachable.add(nxt)
                queue.append(nxt)

    output: Grid = [[8] * w for _ in range(h)]
    for r, c in reachable:
        output[r][c] = 2
    return output


def solve_5961cc34(grid: Grid) -> Grid:
    motifs = extractMotifs(grid)
    filtered = filterByGuideCount(motifs)
    guide_graph = buildGuideGraph(grid, filtered)
    return propagateScaffold(guide_graph)


p = solve_5961cc34
