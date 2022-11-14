import copy
import os
from satsolver import dpll, dimacs, Model, Conjunction, verify_model, puzzle
from tests.conftest import ROOT_DIR
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


def test_sudoku_examples__4x4():
    """Verify dpll can solve set of 4x4 examples."""
    fname = os.path.join(ROOT_DIR, "datasets/4x4.txt")
    assert os.path.exists(fname)

    rules = dimacs.parse_file(os.path.join(ROOT_DIR, "rules/sudoku-rules-4x4.cnf"))

    passed = 0
    with open(fname, "r") as f:
        for line in f.readlines():
            if not line:
                continue
            if line[-1] == "\n":
                line = line[:-1]
            # line.replace("\n", "")
            system = puzzle.encode_puzzle(line)
            system += rules
            model: Model = {}
            res = dpll.dpll(system, model)
            assert res

            valid, reason = verify_model(system, model)
            assert valid
            passed += 1

            # print(puzzle.visualize_sudoku_model(model, board_size=4))

        print(f"{passed} 4x4 examples passed!")
