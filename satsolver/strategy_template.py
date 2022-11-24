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


def simplify(
    system: Conjunction,
    model: Model,
    tautologies: bool = True,
    unit_clauses: bool = True,
) -> Tuple[bool, Dict]:
    """
    Like dpll.py.simplify() except it reports some stats about each literals occurences.
    (e.g. for computing "purity ratio").
    """
    # logging.debug(f"in simplify, system = {system}\n")
    i = 0
    # all_literals = set()
    run_again = False

    # map each literal to a dict of stats
    literal_stats = {}

    while True:
        if i > len(system) - 1:
            break
        clause = system[i]

        # handle tautologies e.g. {111, -111, 114}
        if tautologies:
            new_clause = set([t for t in clause if -t not in clause])
            # removed_tokens = clause - new_clause  # e.g. {111, -111}
            system[i] = new_clause
            clause = system[i]

        if len(clause) == 0:
            system.pop(i)
            continue

        # apply model to simplify if possible
        remove_tokens = set()
        clause_removed = False
        for t in clause:
            if abs(t) in model:
                term_val = model[abs(t)] if t > 0 else not model[abs(t)]
                if term_val == True:  # whole clause must be true
                    # logging.debug(
                    #    f"removing clause (known to be true from model): {clause}"
                    # )
                    system.pop(i)
                    clause_removed = True
                    break
                else:
                    # logging.debug(
                    #    f"removing useless token {t} (where {abs(t)} = {model[abs(t)]}) from clause: {clause}"
                    # )
                    remove_tokens.add(t)
        if clause_removed:
            continue
        # if remove_tokens:
        #    logging.debug(f"remove_tokens = {remove_tokens}")
        if len(clause) == len(remove_tokens):
            return False, set()  # inconsistent (no terms left to make clause true)
        system[i] = clause - remove_tokens
        clause = system[i]

        # handle unit clauses
        if unit_clauses and len(clause) == 1:
            term = list(clause)[0]  # e.g. -124
            term_value = term > 0
            if abs(term) in model and model[abs(term)] != term_value:
                return False, set()  # inconsistent
            model[abs(term)] = term_value  # update model, ensuring this clause is True
            system.pop(i)
            run_again = True
            continue

        # track stats about all literals (still in system)
        for t in clause:
            if abs(t) not in literal_stats:
                literal_stats[abs(t)] = {
                    "clause_lengths": [],
                    "cp": 0,  # num occurences as positive literal
                    "cn": 0,  # num occurences as negative literal
                }
            literal_stats[abs(t)]["cp" if t > 0 else "cn"] += 1
            literal_stats[abs(t)]["clause_lengths"].append(len(clause))
        i += 1

    if run_again:
        # there may be new unit clauses to handle:
        logging.debug("simplify: calling itself recursively")
        return simplify(system, model, tautologies=False, unit_clauses=True)
    return True, literal_stats
