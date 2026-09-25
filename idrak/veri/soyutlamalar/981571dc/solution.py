
from __future__ import annotations

from typing import List, Tuple

import numpy as np


Grid = List[List[int]]


def _complete_lines_once(arr: np.ndarray) -> tuple[np.ndarray, bool]:
    n = arr.shape[0]
    arr = arr.copy()
    changed = False

    for i in range(n):
        row = arr[i]
        mask = row != 0
        if mask.all():
            continue

        candidates: list[tuple[int, int, int, np.ndarray]] = []

        for j in range(n):
            if j == i:
                continue
            other = arr[j]
            if np.all(other[mask] == row[mask]):
                zero_count = int(np.sum(other == 0))
                candidates.append((zero_count, 0, j, other.copy()))

        for j in range(n):
            col = arr[:, j]
            if np.all(col[mask] == row[mask]):
                zero_count = int(np.sum(col == 0))
                candidates.append((zero_count, 1, j, col.copy()))

        if not candidates:
            continue

        _, _, _, source = min(candidates, key=lambda item: (item[0], item[1], item[2]))
        before = row.copy()
        row[~mask] = source[~mask]
        if not np.array_equal(before, row):
            changed = True

    return arr, changed


def fillIncompleteLines(grid: Grid) -> Tuple[Grid, bool]:
    arr = np.array(grid, dtype=int)
    arr2, changed = _complete_lines_once(arr)
    return arr2.tolist(), changed


def iterateCompletion(grid: Grid) -> Grid:
    arr = np.array(grid, dtype=int)
    while True:
        arr, ch1 = _complete_lines_once(arr)
        arr_t, ch2 = _complete_lines_once(arr.T)
        arr = arr_t.T
        if not (ch1 or ch2):
            break
    return arr.tolist()


def mirrorDiagonalZeros(grid: Grid) -> Grid:
    arr = np.array(grid, dtype=int)
    n = arr.shape[0]
    for i in range(n):
        for j in range(i + 1, n):
            if arr[i, j] == 0 and arr[j, i] != 0:
                arr[i, j] = arr[j, i]
            elif arr[j, i] == 0 and arr[i, j] != 0:
                arr[j, i] = arr[i, j]
    return arr.tolist()


def solve_981571dc(grid: Grid) -> Grid:
    filled, _ = fillIncompleteLines(grid)
    completed = iterateCompletion(filled)
    return mirrorDiagonalZeros(completed)


p = solve_981571dc
