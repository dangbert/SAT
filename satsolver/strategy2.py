import copy
from satsolver import Disjunction, Conjunction, Model, puzzle
from satsolver import strategy_template

# from satsolver.dpll import simplify
from typing import MutableSet, Tuple, Dict
import logging


def select_lowest_purity(literal_stats: Dict) -> Tuple[int, bool]:
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


solver = strategy_template.strategy_template(
    strategy_template.simplify, select_lowest_purity
)


###### extra methods used to compare against select_lowest_purity:


def select_lowest_purity__reversed(literal_stats: Dict) -> Tuple[int, bool]:
    """
    Same as select_lowest_purity, but reverse the initial guess.
    i.e. if var is 60% negative in its occurences, take the initial guess to be True (instead of False).
    """
    var, guess = select_lowest_purity(literal_stats)
    return var, not guess


def select_highest_purity(literal_stats: Dict) -> Tuple[int, bool]:
    """
    Like select_lowest_purity, but selects the highest purity variable.
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

    data = sorted(purities.keys(), key=lambda x: -purities[x]["ratio"])  # descending
    # data = sorted(purities.keys(), key=lambda x: purities[x]["ratio"])  # ascending
    return data[0], purities[data[0]]["guess"]


def select_highest_purity__reversed(literal_stats: Dict) -> Tuple[int, bool]:
    """
    Same as select_highest_purity, but reverse the initial guess.
    i.e. if var is 90% negative in its occurences, take the initial guess to be True (instead of False).
    """
    var, guess = select_highest_purity(literal_stats)
    return var, not guess
