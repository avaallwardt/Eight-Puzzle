"""Explore the 8-puzzle's state graph with BFS and compare BFS against A*."""

from __future__ import annotations

import random
import statistics
import time
from collections import Counter

from .board import format_board, is_solvable, random_board
from .solver import distances_from_goal, search_astar, search_bfs


def report(samples: int = 50, seed: int = 0, out=print) -> None:
    start = time.perf_counter()
    dist = distances_from_goal()
    elapsed = time.perf_counter() - start

    out(f"BFS from the goal reached {len(dist):,} boards in {elapsed:.2f}s")
    out("(exactly half of the 9! = 362,880 arrangements, as the parity rule predicts)\n")

    counts = Counter(dist.values())
    widest = max(counts.values())
    out("Optimal solution length -> number of boards")
    for depth in sorted(counts):
        bar = "#" * max(1, round(40 * counts[depth] / widest))
        out(f"  {depth:>2}  {counts[depth]:>6,}  {bar}")

    hardest = max(counts)
    out(f"\nHardest boards ({hardest} moves):")
    for board in (b for b, d in dist.items() if d == hardest):
        out(format_board(board) + "\n")

    rng = random.Random(seed)
    boards = []
    while len(boards) < samples:
        board = random_board(rng)
        if is_solvable(board):
            boards.append(board)

    bfs = [search_bfs(b).expanded for b in boards]
    astar = [search_astar(b).expanded for b in boards]
    out(f"Nodes expanded on {samples} random solvable boards (median):")
    out(f"  BFS              {statistics.median(bfs):>9,.0f}")
    out(f"  A* (Manhattan)   {statistics.median(astar):>9,.0f}")
    out(f"  -> A* expands {statistics.median(b / a for b, a in zip(bfs, astar)):.0f}x fewer nodes")
