import random

from eight_puzzle.board import GOAL, apply_move, is_solvable, random_board
from eight_puzzle.solver import (
    distances_from_goal,
    manhattan,
    min_moves,
    search_astar,
    search_bfs,
    solve_astar,
    solve_bfs,
)

HARDEST = (8, 6, 7, 2, 5, 4, 3, 0, 1)  # one of two boards needing 31 moves


def replay(board, moves):
    for m in moves:
        board = apply_move(board, m)
    return board


def test_already_solved():
    assert solve_astar(GOAL) == []
    assert solve_bfs(GOAL) == []


def test_unsolvable_returns_none():
    swapped = (2, 1, 3, 4, 5, 6, 7, 8, 0)
    assert solve_astar(swapped) is None
    assert solve_bfs(swapped) is None
    assert min_moves(swapped) is None


def test_hardest_board_is_31_moves():
    path = solve_astar(HARDEST)
    assert len(path) == 31
    assert replay(HARDEST, path) == GOAL


def test_astar_matches_bfs_on_random_boards():
    rng = random.Random(0)
    checked = 0
    while checked < 30:
        board = random_board(rng)
        if not is_solvable(board):
            continue
        a, b = solve_astar(board), solve_bfs(board)
        assert len(a) == len(b)
        assert replay(board, a) == GOAL
        checked += 1


def test_manhattan_is_admissible_lower_bound():
    assert manhattan(GOAL) == 0
    assert manhattan(HARDEST) <= 31


def test_distance_table_matches_astar():
    dist = distances_from_goal()
    assert len(dist) == 181440
    assert max(dist.values()) == 31
    assert dist[HARDEST] == 31
    rng = random.Random(1)
    for board in rng.sample(sorted(dist), 20):
        assert len(solve_astar(board)) == dist[board]


def test_astar_expands_fewer_nodes_than_bfs():
    assert search_astar(HARDEST).expanded < search_bfs(HARDEST).expanded
