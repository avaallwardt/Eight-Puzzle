"""Shortest-solution search for the 8-puzzle.

Two solvers that return the same (optimal) answer:

* ``solve_bfs``: breadth-first search over the state graph. Simple, and
  optimal because every move costs 1. It can explore all 181,440 reachable
  states in the worst case.
* ``solve_astar``: A* with the Manhattan-distance heuristic. The heuristic
  never overestimates (each tile needs at least that many moves to get home),
  so A* is still optimal while expanding far fewer states. The game uses this.

Plus ``distances_from_goal``, a single BFS from the goal that labels every
solvable board with its optimal solution length.
"""

from __future__ import annotations

import functools
import heapq
import itertools
from collections import deque
from typing import NamedTuple

from .board import BLANK, GOAL, SIZE, Board, Move, is_solvable, neighbors

# GOAL_POS[tile] = (row, col) where that tile belongs.
GOAL_POS = {tile: divmod(i, SIZE) for i, tile in enumerate(GOAL)}


def manhattan(board: Board) -> int:
    total = 0
    for i, tile in enumerate(board):
        if tile != BLANK:
            r, c = divmod(i, SIZE)
            gr, gc = GOAL_POS[tile]
            total += abs(r - gr) + abs(c - gc)
    return total


def _path(parents: dict[Board, tuple[Board, Move] | None], end: Board) -> list[Move]:
    moves = []
    while parents[end] is not None:
        end, move = parents[end]
        moves.append(move)
    moves.reverse()
    return moves


class SearchResult(NamedTuple):
    path: list[Move] | None  # None if the board is unsolvable
    expanded: int  # number of boards taken off the queue/heap


def search_bfs(start: Board) -> SearchResult:
    if not is_solvable(start):
        return SearchResult(None, 0)
    parents: dict[Board, tuple[Board, Move] | None] = {start: None}
    queue = deque([start])
    expanded = 0
    while queue:
        board = queue.popleft()
        expanded += 1
        if board == GOAL:
            return SearchResult(_path(parents, board), expanded)
        for move, nxt in neighbors(board):
            if nxt not in parents:
                parents[nxt] = (board, move)
                queue.append(nxt)
    raise AssertionError("solvable board never reached the goal")


def search_astar(start: Board) -> SearchResult:
    if not is_solvable(start):
        return SearchResult(None, 0)
    tie = itertools.count()  # breaks ties so heapq never compares boards
    parents: dict[Board, tuple[Board, Move] | None] = {start: None}
    best_g = {start: 0}
    frontier = [(manhattan(start), next(tie), start)]
    expanded = 0
    while frontier:
        _, _, board = heapq.heappop(frontier)
        expanded += 1
        if board == GOAL:
            return SearchResult(_path(parents, board), expanded)
        g = best_g[board] + 1
        for move, nxt in neighbors(board):
            if g < best_g.get(nxt, g + 1):
                best_g[nxt] = g
                parents[nxt] = (board, move)
                heapq.heappush(frontier, (g + manhattan(nxt), next(tie), nxt))
    raise AssertionError("solvable board never reached the goal")


def solve_bfs(start: Board) -> list[Move] | None:
    """Return a shortest list of moves from start to GOAL, or None if unsolvable."""
    return search_bfs(start).path


def solve_astar(start: Board) -> list[Move] | None:
    """Same contract as solve_bfs, using A* with the Manhattan heuristic."""
    return search_astar(start).path


solve = solve_astar


@functools.cache
def distances_from_goal() -> dict[Board, int]:
    """BFS outward from GOAL once, recording every reachable board's distance.

    Every move can be undone, so the distance from GOAL to a board equals the
    board's distance to GOAL. One BFS (~0.5 s) gives the optimal solution
    length for all 181,440 solvable boards. The game uses this table to pick
    puzzles of a chosen difficulty.
    """
    dist = {GOAL: 0}
    queue = deque([GOAL])
    while queue:
        board = queue.popleft()
        for _, nxt in neighbors(board):
            if nxt not in dist:
                dist[nxt] = dist[board] + 1
                queue.append(nxt)
    return dist


def min_moves(start: Board) -> int | None:
    path = solve(start)
    return None if path is None else len(path)
