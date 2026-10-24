"""Board representation and the solvability invariant for the 8-puzzle.

A board is a tuple of the 9 integers 0-8 in row-major order, where 0 is the
blank. Tuples are immutable and hashable, so boards can be used directly as
keys in the solver's visited set.
"""

from __future__ import annotations

import random
from enum import Enum

SIZE = 3
BLANK = 0
GOAL: tuple[int, ...] = (1, 2, 3, 4, 5, 6, 7, 8, BLANK)

Board = tuple[int, ...]


class Move(Enum):
    """A direction the *blank* moves in. Value is (row delta, col delta)."""

    UP = (-1, 0)
    DOWN = (1, 0)
    LEFT = (0, -1)
    RIGHT = (0, 1)


def random_board(rng: random.Random | None = None) -> Board:
    """Return a uniformly random arrangement of the tiles (may be unsolvable)."""
    tiles = list(GOAL)
    (rng or random).shuffle(tiles)
    return tuple(tiles)


def count_inversions(board: Board) -> int:
    """Count pairs of tiles (i before j) with board[i] > board[j], ignoring the blank."""
    tiles = [t for t in board if t != BLANK]
    return sum(
        1
        for i in range(len(tiles))
        for j in range(i + 1, len(tiles))
        if tiles[i] > tiles[j]
    )


def is_solvable(board: Board) -> bool:
    """A 3x3 board is solvable iff its inversion count is even.

    Why this is an invariant: a horizontal move doesn't change the order of the
    tiles at all. A vertical move jumps one tile over the other 2 tiles in its
    row, which changes the inversion count by -2, 0, or +2. Either way the
    parity never changes. The goal has 0 inversions (even), so a board with
    an odd count can never reach it. (The converse, that every even board is
    reachable, is checked exhaustively in the tests.)
    """
    return count_inversions(board) % 2 == 0


def is_solved(board: Board) -> bool:
    return board == GOAL


def valid_moves(board: Board) -> list[Move]:
    row, col = divmod(board.index(BLANK), SIZE)
    return [
        m
        for m in Move
        if 0 <= row + m.value[0] < SIZE and 0 <= col + m.value[1] < SIZE
    ]


def apply_move(board: Board, move: Move) -> Board:
    """Return a new board with the blank moved. Raises ValueError if off the edge."""
    blank = board.index(BLANK)
    row, col = divmod(blank, SIZE)
    new_row, new_col = row + move.value[0], col + move.value[1]
    if not (0 <= new_row < SIZE and 0 <= new_col < SIZE):
        raise ValueError(f"can't move the blank {move.name.lower()} from here")
    target = new_row * SIZE + new_col
    tiles = list(board)
    tiles[blank], tiles[target] = tiles[target], tiles[blank]
    return tuple(tiles)


def neighbors(board: Board) -> list[tuple[Move, Board]]:
    """All boards reachable in one legal move, paired with the move that gets there."""
    return [(m, apply_move(board, m)) for m in valid_moves(board)]


def format_board(board: Board) -> str:
    rows = []
    for r in range(SIZE):
        cells = board[r * SIZE : (r + 1) * SIZE]
        rows.append(" ".join("_" if t == BLANK else str(t) for t in cells))
    return "\n".join(rows)
