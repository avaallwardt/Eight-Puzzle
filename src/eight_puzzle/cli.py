"""Terminal game: decide whether a random board is solvable, then solve it."""

from __future__ import annotations

import argparse
import random
from collections.abc import Callable

from . import board as b
from .solver import distances_from_goal, solve

# Optimal-solution-length ranges, measured with a BFS over every board.
DIFFICULTY = {"easy": range(1, 11), "medium": range(11, 21), "hard": range(21, 32)}

# ESDF layout (like WASD, shifted one key right). Keys move the blank.
KEYS = {"e": b.Move.UP, "d": b.Move.DOWN, "s": b.Move.LEFT, "f": b.Move.RIGHT}
KEY_FOR = {move: key for key, move in KEYS.items()}

HELP = """\
Move the blank (_):
  e = up    d = down    s = left    f = right
Other commands:
  h = hint (best next move)    g = give up (show an optimal solution)
  n = new puzzle               ? = show this help    q = quit"""


class Quit(Exception):
    pass


class Game:
    def __init__(
        self,
        rng: random.Random | None = None,
        input_fn: Callable[[str], str] = input,
        output_fn: Callable[[str], None] = print,
        difficulty: str | None = None,
    ):
        self.rng = rng or random.Random()
        self.difficulty = difficulty
        self._pool: list[b.Board] = []
        if difficulty:
            depths = DIFFICULTY[difficulty]
            self._pool = sorted(bd for bd, d in distances_from_goal().items() if d in depths)
        self._input = input_fn
        self.say = output_fn

    def ask(self, prompt: str) -> str:
        try:
            answer = self._input(prompt).strip().lower()
        except EOFError:
            raise Quit from None
        if answer == "q":
            raise Quit
        return answer

    def run(self) -> None:
        self.say("Welcome to the 8-puzzle! Enter q at any time to quit.")
        self.say(
            "Goal: put the tiles in order 1-8 with the blank (_) in the bottom-right,\n"
            "by sliding the blank into a neighboring tile.\n"
        )
        try:
            while True:
                self.play_round(self.new_board())
        except Quit:
            self.say("Thanks for playing!")

    def new_board(self) -> b.Board:
        if not self.difficulty:
            return b.random_board(self.rng)
        board = self.rng.choice(self._pool)
        if self.rng.random() < 0.5:
            # Swapping two tiles flips the inversion parity, so the board becomes
            # unsolvable while looking about as scrambled as the original.
            i, j = self.rng.sample([k for k, t in enumerate(board) if t != b.BLANK], 2)
            tiles = list(board)
            tiles[i], tiles[j] = tiles[j], tiles[i]
            board = tuple(tiles)
        return board

    def play_round(self, board: b.Board) -> None:
        self.say(b.format_board(board) + "\n")
        solvable = b.is_solvable(board)
        answer = self.ask("Is this puzzle solvable? (y/n) ")
        while answer not in ("y", "yes", "n", "no"):
            answer = self.ask("Please enter y or n: ")
        guessed_solvable = answer.startswith("y")

        if not solvable:
            verdict = "Incorrect" if guessed_solvable else "Correct"
            self.say(
                f"{verdict}! It has {b.count_inversions(board)} inversions, an odd "
                "number, so it can never be solved. Here's a new one.\n"
            )
            return

        self.say(("You're right!" if guessed_solvable else "Actually, it is solvable!") + " Try to solve it.")
        self.say(HELP + "\n")
        self.solve_interactively(board)

    def solve_interactively(self, board: b.Board) -> None:
        optimal = len(solve(board))
        moves_made = 0
        while not b.is_solved(board):
            cmd = self.ask("Your move: ")
            if cmd in KEYS:
                try:
                    board = b.apply_move(board, KEYS[cmd])
                except ValueError:
                    self.say("You can't move the blank that way.")
                    continue
                moves_made += 1
                self.say(b.format_board(board) + "\n")
            elif cmd == "h":
                self.say(f"Hint: {KEY_FOR[solve(board)[0]]}")
            elif cmd == "g":
                path = solve(board)
                keys = " ".join(KEY_FOR[m] for m in path)
                self.say(f"Optimal solution from here ({len(path)} moves): {keys}\n")
                return
            elif cmd == "n":
                self.say("Skipping to a new puzzle.\n")
                return
            elif cmd == "?":
                self.say(HELP)
            else:
                self.say("Unknown command. Enter ? for help.")

        if moves_made == optimal:
            self.say(f"Solved in {moves_made} moves, which is optimal! Great job!\n")
        else:
            self.say(f"Solved in {moves_made} moves! (The shortest solution was {optimal}.)\n")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="eight-puzzle", description="Play the 8-puzzle in your terminal.")
    parser.add_argument("--seed", type=int, help="seed the random puzzle generator (for repeatable games)")
    parser.add_argument(
        "--difficulty",
        choices=DIFFICULTY,
        help="pick puzzles by optimal solution length: easy 1-10, medium 11-20, hard 21-31 moves",
    )
    parser.add_argument(
        "--analyze",
        action="store_true",
        help="instead of playing, BFS the whole state space and benchmark BFS vs A*",
    )
    args = parser.parse_args(argv)
    if args.analyze:
        from .analyze import report

        report(seed=args.seed or 0)
        return
    Game(rng=random.Random(args.seed), difficulty=args.difficulty).run()


if __name__ == "__main__":
    main()
