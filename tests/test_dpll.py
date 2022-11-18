import copy
import os
from satsolver import dpll, dimacs, Model, Conjunction, verify_model, puzzle
from tests.conftest import ROOT_DIR, RULES_4X4, RULES_9X9
import logging


def test_simplify__unit_clauses__easy():
    system: Conjunction = [
        set([111, 112, 114]),
        set([-115]),
        set([-111, -113]),
    ]
    expected: Conjunction = [
        set([111, 112, 114]),
        set([-111, -113]),
    ]
    args = {"unit_clauses": True, "tautologies": False}
    model: Model = {}
    dpll.simplify(system, model, **args)
    assert system == expected
    assert model == {115: False}


def test_simplify__unit_clauses__complicated():
    args = {"unit_clauses": True, "tautologies": False}

    # test other clauses get updated
    system: Conjunction = [
        set([111, 112, 114]),
        set([-111, -113, 115]),
        set([-115]),
    ]
    expected: Conjunction = [
        set([111, 112, 114]),
        set([-111, -113]),
    ]
    model = {}
    dpll.simplify(system, model, **args)
    assert system == expected
    assert model == {115: False}

    # test other clauses get updated (removed when needed)
    system = [
        set([111, 112, 114]),
        set([-111, -113, -115]),
        set([-115]),
    ]
    expected = [
        set([111, 112, 114]),
    ]
    model = {}
    dpll.simplify(system, model, **args)
    assert system == expected
    assert model == {115: False}

    # harder test3 (removal of 115 -> 111 can also be removed)
    system: Conjunction = [
        set([-111, 112, 114]),
        set([111, 115]),
        set([-115]),
    ]
    expected: Conjunction = [
        set([112, 114]),
    ]
    model: Model = {}
    dpll.simplify(system, model, **args)
    assert system == expected
    assert model == {115: False, 111: True}


def test_simplify__tautologies():
    system: Conjunction = [
        set([111, 112, 114]),
        set([113, -111, -113]),
        set([-115]),
        set([5, -111, 111, 17]),
    ]
    expected: Conjunction = [
        set([111, 112, 114]),
        set([-111]),
        set([-115]),
        set([5, 17]),
    ]
    args = {"unit_clauses": False, "tautologies": True}
    model: Model = {}
    dpll.simplify(system, model, **args)
    assert system == expected
    assert model == {}


def test_simplify__finds_pure_literals():
    system: Conjunction = [
        set([-111, 112]),
        set([-111, -115, -112]),
        set([115]),
        set([-111, 117]),
    ]
    cur = copy.deepcopy(system)
    args = {"unit_clauses": False, "tautologies": False}
    model: Model = {}

    res, pure = dpll.simplify(cur, model, **args)
    assert system == cur and model == {}, "unchanged"
    assert res and pure == {-111, 117}

    system.append(set([113]))
    cur = copy.deepcopy(system)
    res, pure = dpll.simplify(cur, model, **args)
    assert system == cur and model == {}, "unchanged"
    assert res and pure == {-111, 117, 113}


def test_sudoku_examples__4x4():
    """Verify dpll can solve set of 4x4 examples."""
    fname = os.path.join(ROOT_DIR, f"datasets/4x4.txt")
    sudoku_tester(RULES_4X4, fname, 4)


def test_sudoku_examples__9x9_few():
    """Verify dpll can solve set of 9x9 examples."""
    rules = dimacs.parse_file(RULES_9X9)

    passed = 0
    for n in range(1, 5 + 1):
        fname = os.path.join(ROOT_DIR, f"example_sudokus/sudoku{n}.cnf")
        system = dimacs.parse_file(fname) + rules
        model: Model = {}

        res, stats = dpll.solver(system, model)
        assert res
        valid, reason = verify_model(system, model)
        assert valid
        passed += 1
    print(f"{passed} 9x9 examples passed!")


# def test_sudoku_examples__9x9_many():
#    """Verify dpll can solve set of 9x9 examples."""
#    fnames = [
#        "damnhard.sdk.txt",
#        "top91.sdk.txt",
#        "top95.sdk.txt",
#        "top100.sdk.txt",
#        "top870.sdk.txt",
#        "1000 sudokus.txt",
#        "top2365.sdk.txt",
#    ]
#    for fname in fnames:
#        print("running on file: " + fname)
#        fname = os.path.join(ROOT_DIR, "datasets", fname)
#        assert os.path.exists(fname)
#        sudoku_tester(RULES_9X9, fname, 9)


def sudoku_tester(
    rules_path: str, dataset_path: str, board_size: int, report_stats: bool = False
):
    """Helper function."""
    size_desc = f"{board_size}x{board_size}"
    rules = dimacs.parse_file(rules_path)

    passed = 0
    with open(dataset_path, "r") as f:
        for line in f.readlines():
            if not line:
                continue
            line = line.replace("\n", "")
            system = puzzle.encode_puzzle(line)
            system += rules
            model: Model = {}
            res, stats = dpll.solver(system, model)
            assert res
            if report_stats:
                print(stats)

            valid, reason = verify_model(system, model)
            assert valid
            passed += 1
            # print("\n" + "".join(["_" for _ in range(board_size * 2)]))
            # print(puzzle.visualize_sudoku_model(model, board_size=board_size))

        print(f"{passed} {size_desc} examples passed!")
