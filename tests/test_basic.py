from satsolver import puzzle, Conjunction, Model, verify_model, model_to_system


def test_verify_model():
    system: Conjunction = [
        set([111, 112]),
        set([-111, 113]),
    ]
    model: Model = {111: False, 112: True}
    res, reason = verify_model(system, model)
    assert not res and reason == "var 113 not in model"

    model[113] = True
    res, reason = verify_model(system, model)
    assert res and reason == "system/model is True"

    model[112] = False
    res, reason = verify_model(system, model)
    assert not res and reason == "system/model is False"


def test_parsing_sudoko():
    """Test parsing of strings to sudoku."""

    # 4x4 examples:
    sudoku = "...3..4114..3..."
    res = puzzle.encode_puzzle(sudoku)
    assert res == [{143}, {234}, {241}, {311}, {324}, {413}]

    sudoku = "1.3....44....3.1"
    res = puzzle.encode_puzzle(sudoku)
    assert res == [{111}, {133}, {244}, {314}, {423}, {441}]

    # 9x9:
    sudoku = "53..97..........7.....1..5......13....4..2...1.98..2.4........5.7....92..91.5...."
    res = puzzle.encode_puzzle(sudoku)
    vals = [
        115,
        123,
        159,
        167,
        287,
        351,
        385,
        461,
        473,
        534,
        562,
        611,
        639,
        648,
        672,
        694,
        795,
        827,
        879,
        882,
        929,
        931,
        955,
    ]
    assert res == [{t} for t in vals]


def test_visualize_sudoku_model():
    # sudoku = "...3..4114..3..."
    model = {143: True, 234: True, 241: True, 311: True, 324: True, 413: True}
    res = puzzle.visualize_sudoku_model(model, 4)
    print(res)
    # expected = "? ? ? 3 \n? ? 4 1 \n1 4 ? ? \n3 ? ? ? \n"
    expected = "? ?  ? 3 \n? ?  4 1 \n\n1 4  ? ? \n3 ?  ? ? \n"
    assert res == expected

    # more realistic/complete model:
    model[141] = False
    model[142] = False
    model[144] = False
    res = puzzle.visualize_sudoku_model(model, 4)
    assert res == expected
