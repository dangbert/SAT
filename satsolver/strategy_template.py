import copy
from satsolver import Disjunction, Conjunction, Model, puzzle

# from satsolver.dpll import simplify
from typing import MutableSet, Tuple, Dict
import logging
from collections.abc import Callable


type_simplify = Callable  # [[Conjunction, Model, bool, bool], Tuple[int, Dict]]

type_select_split = Callable  # [[Dict], Tuple[int, bool]]


def strategy_template(
    simplify: type_simplify,
    heuristic: type_select_split,
) -> Callable:  # [[Conjunction, Model], Tuple[bool, Dict]]:
    """
    Generates and returns a SAT solver function that uses the provided heuristic and simplify function.
    The stats returned by a call to simplify should be compatible with the stats expected by the heuristic function.
    (Function generator for a generic satsolver).
    """

    def strategy(system: Conjunction, model: Model) -> Tuple[bool, Dict]:
        stats: Dict = {
            "backtracks": 0,
            "pure_literals_used": 0,
        }

        def _solver(
            system: Conjunction,
            model: Model,
            remove_tautologies: bool = False,
        ) -> bool:
            nonlocal stats  # https://stackoverflow.com/a/11987499
            # nonlocal heuristic
            # nonlocal simplify

            # print(puzzle.visualize_sudoku_model(model, board_size=9))
            valid, literal_stats = simplify(
                system, model, tautologies=remove_tautologies
            )
            if not valid:
                stats["backtracks"] += 1
                return False

            if len(system) == 0:
                logging.debug(f"reached an empty system")
                return True

            # choose a variable e.g. -113 to assume its value
            var, init_guess = heuristic(literal_stats)
            logging.debug(
                f"splitting on variable {var} with initial guess: {init_guess}"
            )

            new_system = copy.deepcopy(system)
            new_model = copy.deepcopy(model)
            new_model[abs(var)] = init_guess
            if not _solver(new_system, new_model):
                logging.debug(f"backtracking! (on var {abs(var)})")
                new_system = copy.deepcopy(system)
                new_model = copy.deepcopy(model)
                new_model[abs(var)] = not init_guess
                # stats["backtracks"] += 1
                if not _solver(new_system, new_model):
                    # stats["backtracks"] += 1
                    return False

            # carefully update sytem and model in place (so change is present in the outer scope/function)
            system[:] = new_system
            model.clear()
            model.update(new_model)
            return True

        # note: as an optimization we only remove tautologies on the first pass
        res = _solver(system, model, remove_tautologies=True)
        return res, stats

    return strategy
