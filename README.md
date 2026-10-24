# 8-Puzzle

[![CI](https://github.com/YOUR-USERNAME/eight-puzzle/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR-USERNAME/eight-puzzle/actions/workflows/ci.yml)

A terminal game built on one question: **can this scrambled 8-puzzle be solved?** First you decide. If it can, you solve it yourself, and an optimal solver can give you hints or the shortest solution.

```
2 _ 3
1 8 5
4 7 6

Is this puzzle solvable? (y/n) y
You're right! Try to solve it.
Your move: h
Hint: s
...
Solved in 7 moves, which is optimal! Great job!
```

## Background

I came up with this game while watching MIT's [6.1200 Mathematics for Computer Science](https://ocw.mit.edu/) lectures on OpenCourseWare. The course introduced the 8-puzzle as the motivation for state machines and the invariant principle. I was first intrigued by the idea of quickly determining solvability by counting the number of inverted pairs on the board. Then I became interested in how to efficiently solve a solvable board.

## How it works

### 1. Solvability is a parity invariant (O(1) for a fixed board size)

Read the tiles row by row and skip the blank. An **inversion** is a pair of tiles in the wrong relative order.

- A **horizontal** move never changes the reading order, so the inversion count stays the same.
- A **vertical** move jumps one tile over the other two tiles in its row. That changes the count by −2, 0, or +2.

So the **parity** of the inversion count never changes. The goal has 0 inversions (even), so a board with an odd count is unsolvable. The other direction, that every even board *is* solvable, is harder to prove by hand. The test suite checks it by brute force: a BFS reaches exactly the 181,440 even boards and none of the odd ones (`tests/test_board.py`).

### 2. BFS over the whole state graph

Every board is a node, and every legal move is an edge between two boards. Moves can always be undone, so one BFS **outward from the goal** gives the optimal solution length of *every* solvable board at once, in under a second (`distances_from_goal` in `solver.py`). That table powers:

- **Difficulty levels**: `--difficulty hard` deals boards that need 21 to 31 moves. Half of them get two tiles swapped, which flips the parity and makes the board unsolvable, so you still have to check.
- **State-space analysis**: `eight-puzzle --analyze`

```
BFS from the goal reached 181,440 boards in 0.74s
Optimal solution length -> number of boards
  ...
  22  23,952  ########################################
  23  20,224  ##################################
  24  24,047  ########################################
  ...
  31       2  #

Nodes expanded on 50 random solvable boards (median):
  BFS                 83,256
  A* (Manhattan)         672
  -> A* expands 88x fewer nodes
```

### 3. Optimal solving: BFS vs. A*

| Solver | Idea | Why it's optimal |
|---|---|---|
| `solve_bfs` | Explore boards in order of distance from the start | Every move costs 1, so the first time BFS reaches the goal, it got there by a shortest path |
| `solve_astar` | Expand the board with the lowest *moves so far + Manhattan distance* first | Manhattan distance never overestimates (each tile needs at least that many moves), and it is consistent |

Both return the same lengths (tested). A* expands about 90× fewer nodes, so the game uses it for hints and "give up".

## Usage

Requires Python 3.10+.

```bash
git clone https://github.com/YOUR-USERNAME/eight-puzzle.git
cd eight-puzzle
pip install -e .

eight-puzzle                       # random boards
eight-puzzle --difficulty medium   # easy | medium | hard
eight-puzzle --seed 42             # repeatable games
eight-puzzle --analyze             # BFS state-space report
```

Or run it without installing: `python -m eight_puzzle` from inside `src/`.

**Controls** (ESDF, like WASD shifted one key right; keys move the blank)

| Key | Action | Key | Action |
|---|---|---|---|
| `e` | up | `h` | hint |
| `d` | down | `g` | give up: show an optimal solution |
| `s` | left | `n` | skip to a new puzzle |
| `f` | right | `?` | help · `q` quit |

## Project layout

```
src/eight_puzzle/
  board.py    immutable board (tuple), moves, inversion parity
  solver.py   BFS, A*, and the BFS distance table
  cli.py      game loop (input/output are injectable for testing)
  analyze.py  --analyze report
tests/        pytest: exhaustive parity check, solver equivalence, scripted games
```

## Development

```bash
pip install -e ".[dev]"
pytest
ruff check .
```

CI runs both on Python 3.10, 3.12, and 3.13.

## Ideas for next steps

- Generalize to the n×n sliding puzzle. The parity rule changes for even widths: the blank's row also counts.
- IDA* for the 15-puzzle, where BFS's memory use stops being practical.
- Pattern-database heuristics.
