from collections.abc import Callable
import os
from satsolver import Model, dimacs, verify_model
from satsolver import strategy2, strategy3, strategy_random
from tests.conftest import ROOT_DIR, RULES_4X4, RULES_9X9
from tests.test_dpll import sudoku_tester


def test_other_strategies():
    """simple test that all the other solvers can run successfully."""
    solvers = [strategy2.solver, strategy3.solver, strategy_random.solver]

    for i, solver in enumerate(solvers):
        fname = os.path.join(ROOT_DIR, f"datasets/4x4.txt")
        print(f"testing other solver {i} on rules: {RULES_4X4}")
        sudoku_tester(RULES_4X4, fname, 4, solver=solver)

        rules = dimacs.parse_file(RULES_9X9)

        passed = 0
        # for n in range(1, 5 + 1):
        for n in range(3, 5):  # for time test on just a few
            fname = os.path.join(ROOT_DIR, f"example_sudokus/sudoku{n}.cnf")
            print("testing on file: " + fname)
            system = dimacs.parse_file(fname) + rules
            model: Model = {}

            res, stats = solver(system, model)
            assert res
            valid, reason = verify_model(system, model)
            assert valid
            passed += 1
        print(f"{passed} 9x9 examples passed!")
