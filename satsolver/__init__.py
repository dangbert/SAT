from typing import MutableSet, List, Dict

# type aliases:
Disjunction = MutableSet[int]

Conjunction = List[Disjunction]

# model (may be partial)
Model = Dict[int, bool]
