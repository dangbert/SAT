import copy
from satsolver import Disjunction, Conjunction, Model, puzzle
from satsolver import strategy_template

# from satsolver.dpll import simplify
from typing import MutableSet, Tuple, Dict
import logging


def select_split(literal_stats: Dict) -> Tuple[int, bool]:
    """Heuristic which picks what variable to split on, and what the initial guess should be.
    The returned variable will always be its positive form.
    E.g. returns (115, False)
    """
    purities = {}
    # purities = { for (k,v) in literal_stats}

    for var in literal_stats:
        cp = literal_stats[var]["cp"]
        cn = literal_stats[var]["cn"]
        purity = max(cp / (cp + cn), cn / (cp + cn))
        purities[abs(var)] = {
            "ratio": purity,
            "guess": cp > cn,
        }

    # data = sorted(purities.keys(), key=lambda x: -purities[x]["ratio"]) # descending
    data = sorted(purities.keys(), key=lambda x: purities[x]["ratio"])  # ascending
    return data[0], purities[data[0]]["guess"]


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


solver = strategy_template.strategy_template(simplify, select_split)
