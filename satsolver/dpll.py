from copy import deepcopy
from satsolver import Disjunction, Conjunction, Model
from typing import MutableSet, Tuple


def dpll(system: Conjunction, model: Model) -> bool:
    """
    Runs the dpll algorithm, returning True if a solution is found.
    The param model will be updated in place to the solution (if any).
    """

    if not simplify(system, model):
        return False

    # remove clauses from α containing literal
    # shorten clauses from α containing ¬literal
    # if (α contains no clauses) return true;
    # if (α contains empty clause return false;

    # choose P in α;
    # if (dpll_2(α, ¬P)) return true;
    # return dpll_2(α, P);

    return True  # TODO


# def simplify_unit_clauses(system: Conjunction, model: Model, tautologies: bool = True, unit_clauses: bool=True, pure_literals:bool=True) -> bool:
def simplify(
    system: Conjunction,
    model: Model,
    tautologies: bool = True,
    unit_clauses: bool = True,
) -> Tuple[bool, MutableSet[int]]:
    """
    Simplifies a system using 3 techiques (or a subset of them), and updating the (ongoing) model.
    returns False if an inconsistency is found.
    also returns the set of pure literals found in the system.

    unit_clauses:
        Simplify the system by removing all unit clauses.

    """
    i = 0
    all_literals = set()
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

        # handle unit clauses
        if unit_clauses and len(clause) == 1:
            term = list(clause)[0]  # e.g. -124
            term_value = term > 0
            if abs(term) in model and model[abs(term)] != term_value:
                return False  # inconsistent
            model[abs(term)] = term_value  # update model, ensuring this clause is True
            system.pop(i)
            continue

        all_literals = all_literals.union(
            clause
        )  # track all literals (still in system)
        i += 1

    pure = set([t for t in all_literals if -t not in all_literals])
    return True, pure


# def simplify_tautologies(system: Conjunction, model: Model) -> None:
#    # TODO
#    return True
#
#
# def simplify_pure_literals(system: Conjunction, model: Model) -> None:
#    # TODO
#    return True
#
