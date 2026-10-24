from collections import deque
from itertools import permutations

import pytest

from eight_puzzle.board import (
    GOAL,
    Move,
    apply_move,
    count_inversions,
    format_board,
    is_solvable,
    neighbors,
    valid_moves,
)


def reachable_from_goal() -> set:
    seen = {GOAL}
    queue = deque([GOAL])
    while queue:
        for _, nxt in neighbors(queue.popleft()):
            if nxt not in seen:
                seen.add(nxt)
                queue.append(nxt)
    return seen


def test_parity_rule_matches_brute_force_on_every_board():
    # Moves are reversible, so "can reach GOAL" == "reachable from GOAL".
    reachable = reachable_from_goal()
    assert len(reachable) == 362880 // 2
    for perm in permutations(range(9)):
        assert is_solvable(perm) == (perm in reachable)


def test_inversions_ignore_blank():
    # Blank sits before tiles 1-8 but should not count as an inversion.
    assert count_inversions((0, 1, 2, 3, 4, 5, 6, 7, 8)) == 0
    assert count_inversions((2, 1, 3, 4, 5, 6, 7, 8, 0)) == 1


def test_valid_moves_in_corner_and_center():
    assert set(valid_moves(GOAL)) == {Move.UP, Move.LEFT}
    center = (1, 2, 3, 4, 0, 5, 6, 7, 8)
    assert set(valid_moves(center)) == set(Move)


def test_apply_move_swaps_and_does_not_mutate():
    board = GOAL
    moved = apply_move(board, Move.LEFT)
    assert moved == (1, 2, 3, 4, 5, 6, 7, 0, 8)
    assert board == GOAL


@pytest.mark.parametrize("move", [Move.DOWN, Move.RIGHT])
def test_apply_move_off_edge_raises(move):
    with pytest.raises(ValueError):
        apply_move(GOAL, move)


def test_format_board():
    assert format_board(GOAL) == "1 2 3\n4 5 6\n7 8 _"
