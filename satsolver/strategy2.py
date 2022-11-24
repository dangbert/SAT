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


solver = strategy_template.strategy_template(strategy_template.simplify, select_split)
simplify = 1
