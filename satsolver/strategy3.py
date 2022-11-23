import copy
from satsolver import Disjunction, Conjunction, Model, puzzle, heuristics
from typing import MutableSet, Tuple, Dict
import logging


def solver(system: Conjunction, model: Model) -> Tuple[bool, Dict]:
    """
    Runs the dpll algorithm, returning a boolean indicating if a solution is found, and a dictionary of stats.
    The params model and system will both be updated in place.
    """

    stats: Dict = {
        "backtracks": 0,
        "pure_literals_used": 0,
    }

    def _solver(
        system: Conjunction, model: Model, remove_tautologies: bool = False
    ) -> bool:
        nonlocal stats  # https://stackoverflow.com/a/11987499

        # print(puzzle.visualize_sudoku_model(model, board_size=9))
        valid, pure = simplify(system, model, tautologies=remove_tautologies)
        if not valid:
            stats["backtracks"] += 1
            return False

        if len(system) == 0:
            logging.debug(f"reached an empty system")
            return True

        # pick literal with dlis
        init_guess = True
        var = heuristics.dlis(system)

        new_system = copy.deepcopy(system)
        new_model = copy.deepcopy(model)
        new_model[(var)] = init_guess
        if not _solver(new_system, new_model):
            logging.debug(f"backtracking! (on var {(var)})")
            new_system = copy.deepcopy(system)
            new_model = copy.deepcopy(model)
            new_model[(var)] = not init_guess
            if not _solver(new_system, new_model):
                return False

        # carefully update sytem and model in place (so change is present in the outer scope/function)
        system[:] = new_system
        model.clear()
        model.update(new_model)
        return True

    # note: as an optimization we only remove tautologies on the first pass
    res = _solver(system, model, remove_tautologies=True)
    return res, stats


def simplify(
    system: Conjunction,
    model: Model,
    tautologies: bool = True,
    unit_clauses: bool = True,
) -> Tuple[bool, MutableSet[int]]:
    """
    Simplifies a system (in place) using 2 techniques (or a subset of them), and updates the (ongoing) model.
    returns False if an inconsistency is found.
    also returns the set of pure literals found in the system (when the system is consistent).

    params:
        system: the logic system
        model: (partial) model for the logic system
        unit_clauses:
            Simplify the system by removing all unit clauses.
        tautologies:
            Simplify the system by removing all tautologies within disjunctions.
    """
    # logging.debug(f"in simplify, system = {system}\n")
    i = 0
    all_literals = set()
    run_again = False
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

        # apply model to simplify if possible
        if len(clause) == 0:
            system.pop(i)
            continue

        remove_tokens = set()
        clause_removed = False
        for t in clause:
            if (t) in model:
                term_val = model[(t)] if t > 0 else not model[(t)]
                if term_val == True:  # whole clause must be true
                    logging.debug(
                        f"removing clause (known to be true from model): {clause}"
                    )
                    system.pop(i)
                    clause_removed = True
                    break
                else:
                    logging.debug(
                        f"removing useless token {t} (where {(t)} = {model[(t)]}) from clause: {clause}"
                    )
                    remove_tokens.add(t)
        if clause_removed:
            continue
        if remove_tokens:
            logging.debug(f"remove_tokens = {remove_tokens}")
        if len(clause) == len(remove_tokens):
            return False, set()  # inconsistent (no terms left to make clause true)
        system[i] = clause - remove_tokens
        clause = system[i]

        # handle unit clauses
        if unit_clauses and len(clause) == 1:
            term = list(clause)[0]  # e.g. -124
            term_value = term > 0
            if (term) in model and model[
            (term)] != term_value:
                return False, set()  # inconsistent
            model[(term)] = term_value  # update model, ensuring this clause is True
            system.pop(i)
            run_again = True
            continue

        all_literals = all_literals.union(
            clause
        )  # track all literals (still in system)
        i += 1

    pure = set([t for t in all_literals if -t not in all_literals])
    if run_again:
        # there may be new unit clauses to handle:
        logging.debug("simplify: calling itself recursively")
        return simplify(system, model, tautologies=False, unit_clauses=True)
    return True, pure
