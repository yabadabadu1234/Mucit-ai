
from __future__ import annotations

from collections import Counter
from typing import List, Sequence, Tuple

Grid = List[List[int]]
Row = List[int]


def _border_color(row: Sequence[int]) -> int:
    return row[0]


def _walkway_color(row: Sequence[int]) -> int | None:
    border = row[0] if row else None
    for v in row:
        if border is not None and v != border:
            return v
    return None


def detectInnerSegment(row: Row) -> List[int]:
    if not row:
        return []
    border = _border_color(row)
    walkway = _walkway_color(row)
    def is_inner(v: int) -> bool:
        return v != border and (walkway is None or v != walkway)

    start = next((i for i, v in enumerate(row) if is_inner(v)), None)
    if start is None:
        return []
    end = next((i for i, v in enumerate(reversed(row)) if is_inner(v)), None)
    if end is None:
        return []
    last = len(row) - 1 - end
    return row[start : last + 1]


def _majority(bucket: Sequence[int]) -> Tuple[int, int]:
    if not bucket:
        return 0, 0
    value, freq = Counter(bucket).most_common(1)[0]
    return value, freq


def enumeratePatterns(segment: List[int]) -> List[Tuple[List[int], Tuple[float, int, int]]]:
    n = len(segment)
    if n == 0:
        return []
    limit = min(6, n)
    candidates: List[Tuple[List[int], Tuple[float, int, int]]] = []
    for p in range(1, limit + 1):
        groups = [[segment[i] for i in range(offset, n, p)] for offset in range(p)]
        pattern: List[int] = []
        mismatch = 0
        for bucket in groups:
            val, freq = _majority(bucket)
            pattern.append(val)
            mismatch += len(bucket) - freq
        score = (mismatch / n, mismatch, p)
        candidates.append((pattern, score))
    return candidates


def selectBestPattern(patterns: List[Tuple[List[int], Tuple[float, int, int]]]) -> Tuple[List[int], Tuple[float, int, int]]:
    if not patterns:
        return ([], (0.0, 0, 0))
    return min(patterns, key=lambda ps: ps[1])


def tileSegment(row: Row, best: Tuple[List[int], Tuple[float, int, int]]) -> Row:
    pattern, (_ratio, _mismatch, p) = best
    if not row or not pattern or p == 0:
        return row[:]
    border = _border_color(row)
    walkway = _walkway_color(row)

    def is_inner(v: int) -> bool:
        return v != border and (walkway is None or v != walkway)

    start = next((i for i, v in enumerate(row) if is_inner(v)), None)
    if start is None:
        return row[:]
    end = next((i for i, v in enumerate(reversed(row)) if is_inner(v)), None)
    if end is None:
        return row[:]
    last = len(row) - 1 - end

    inner_len = last - start + 1
    tiled_inner = [pattern[i % p] for i in range(inner_len)]
    return row[:start] + tiled_inner + row[last + 1 :]


def solve_135a2760(grid: Grid) -> Grid:
    def fixRow(row: Row) -> Row:
        segment = detectInnerSegment(row)
        patterns = enumeratePatterns(segment)
        best = selectBestPattern(patterns)
        return tileSegment(row, best)
    
    return [fixRow(row) for row in grid]


p = solve_135a2760
