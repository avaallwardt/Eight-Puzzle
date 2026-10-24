from eight_puzzle.cli import Game, Quit

ONE_AWAY = (1, 2, 3, 4, 5, 6, 7, 0, 8)  # solved by moving the blank right (f)
UNSOLVABLE = (2, 1, 3, 4, 5, 6, 7, 8, 0)


def make_game(inputs):
    it = iter(inputs)
    out = []

    def fake_input(prompt):
        try:
            return next(it)
        except StopIteration:
            raise EOFError

    return Game(input_fn=fake_input, output_fn=out.append), out


def test_solve_optimally():
    game, out = make_game(["yes", "f"])
    game.play_round(ONE_AWAY)
    assert "optimal" in out[-1]


def test_unsolvable_correct_guess():
    game, out = make_game(["n"])
    game.play_round(UNSOLVABLE)
    assert out[-1].startswith("Correct")


def test_illegal_move_is_rejected_then_game_continues():
    game, out = make_game(["y", "d", "f"])  # blank is on the bottom row
    game.play_round(ONE_AWAY)
    assert "can't move" in " ".join(out)
    assert "Solved" in out[-1]


def test_give_up_shows_solution():
    game, out = make_game(["y", "g"])
    game.play_round(ONE_AWAY)
    assert "(1 moves): f" in out[-1]


def test_quit_mid_round_does_not_move():
    game, _ = make_game(["y", "q"])
    try:
        game.play_round(ONE_AWAY)
    except Quit:
        pass
    else:
        raise AssertionError("expected Quit")


def test_run_exits_cleanly_on_quit():
    game, out = make_game(["q"])
    game.run()
    assert out[-1] == "Thanks for playing!"


def test_difficulty_boards_are_in_range():
    import random

    from eight_puzzle.board import is_solvable
    from eight_puzzle.solver import distances_from_goal

    game = Game(rng=random.Random(3), difficulty="hard")
    dist = distances_from_goal()
    kinds = set()
    for _ in range(40):
        board = game.new_board()
        kinds.add(is_solvable(board))
        if is_solvable(board):
            assert 21 <= dist[board] <= 31
    assert kinds == {True, False}  # both solvable and unsolvable boards show up
