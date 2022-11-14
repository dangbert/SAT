import math
from satsolver import Conjunction, Disjunction, Model, model_to_system


def encode_puzzle(sudoku: str) -> Conjunction:
    """Encodes a string representing a sudoku file into a Conjunction."""

    size = math.sqrt(len(sudoku))
    # assert perfect square
    assert size**2 == len(sudoku) and int(size) == size, f"invalid size = {size}"
    size = int(size)

    clauses: Conjunction = []
    for i, s in enumerate(sudoku):
        if s == ".":
            continue

        # TODO: handle 16x16 hexidecimal
        val = int(s)  # e.g. 8

        # (0 based) indicies into sizexsize sudoku board:
        row_index = int(i // size)
        col_index = i - (row_index * size)

        # +1 because indices are 0 based
        token = int(f"{row_index+1}{col_index+1}{val}")
        clauses.append(set([token]))
    return clauses


def visualize_sudoku_model(model: Model, board_size: int) -> str:
    """Returns a string of a 2D grid representing a model for a sudoku game.
    Note: if the modle is incomplete, question mark will be inserted for unknown squares.
    """
    # system = model_to_system(model)

    box_size = int(math.sqrt(board_size))  # e.g. 2 for 4x4 board
    res = ""
    for row in range(board_size):
        for col in range(board_size):
            # possible values for this location
            symbol = "?"
            for n in range(board_size):
                var = int(f"{row+1}{col+1}{n+1}")
                if var in model and model[var]:
                    symbol = str(n + 1)
                    break
            if col % box_size == 0 and col > 0:
                symbol = f" {symbol}"
            res += symbol + " "
        if (row + 1) % box_size == 0 and row > 0 and row != board_size - 1:
            res += "\n"
        res += "\n"
    return res
