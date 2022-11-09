from copy import deepcopy
from satsolver import Disjunction, Conjunction, Model


def dpll(system: Conjunction, model: Model = {}) -> bool:
    """
    Run the dpll algorithm.
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

    pass  # TODO


# def simplify_unit_clauses(system: Conjunction, model: Model, tautologies: bool = True, unit_clauses: bool=True, pure_literals:bool=True) -> bool:
def simplify(
    system: Conjunction,
    model: Model,
    unit_clauses: bool = True,
    tautologies: bool = True,
    pure_literals: bool = True,
) -> bool:
    """
    Simplifies a system using 3 techiques (or a subset of them), and updating the (ongoing) model.
    returns False if an inconsistency is found.

    unit_clauses:
        Simplify the system by removing all unit clauses.
    """
    i = 0
    while True:
        if i > len(system) - 1:
            break
        clause = system[i]

        # handle unit clauses
        if unit_clauses and len(clause) == 1:
            term = clause[0]  # e.g. -124
            term_value = term > 0
            if abs(term) in model and model[abs(term)] != term_value:
                return False  # inconsistent
            model[abs(term)] = term_value  # update model, ensuring this clause is True
            system.remove(i)
            continue

        if tautologies:
            pass
        if pure_literals:
            pass
        i += 1
    return True


# def simplify_tautologies(system: Conjunction, model: Model) -> None:
#    # TODO
#    return True
#
#
# def simplify_pure_literals(system: Conjunction, model: Model) -> None:
#    # TODO
#    return True
#
