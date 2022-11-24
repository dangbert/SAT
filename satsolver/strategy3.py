import copy
from satsolver import Conjunction, Model
from satsolver import strategy_template
from typing import MutableSet, Tuple, Dict
import logging


def dlis_split(literal_stats: Dict) -> Tuple[int, bool]:
    best_var = max(
        literal_stats.keys(),
        key=lambda x: max(literal_stats[x]["cp"], literal_stats[x]["cn"]),
    )

    guess = literal_stats[best_var]["cp"] > literal_stats[best_var]["cn"]
    return best_var, guess


solver = strategy_template.strategy_template(strategy_template.simplify, dlis_split)
