import copy
import random
from satsolver import Conjunction, Model
from satsolver import strategy_template

from typing import MutableSet, Tuple, Dict
import logging


def select_random(literal_stats: Dict) -> Tuple[int, bool]:
    """Heuristic which picks random variable to split on, and random value for it."""
    return random.choice(list(literal_stats.keys())), random.choice([True, False])


def solver(system: Conjunction, model: Model) -> Tuple[bool, Dict]:
    # return strategy2.solver(system, model, heuristic=select_random)
    func = strategy_template.strategy_template(
        strategy_template.simplify, select_random
    )
    return func(system, model)
