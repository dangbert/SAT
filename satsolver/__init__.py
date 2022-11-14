from typing import MutableSet, List, Dict, Tuple

# type aliases:
Disjunction = MutableSet[int]

Conjunction = List[Disjunction]

# model (may be partial)
Model = Dict[int, bool]


def verify_model(system: Conjunction, model: Model) -> Tuple[bool, str]:
    """Check if a model satisifies a given system.
    Returns True if satisfied and False otherwise (along with a reason).
    """

    res = True
    clause: Disjunction
    for clause in system:
        vals = []
        for t in clause:
            if abs(t) not in model:
                return False, f"var {abs(t)} not in model"
            vals.append(model[abs(t)] if t > 0 else not model[abs(t)])
        res = res and True in vals
    return res, f"system/model is {res}"


def model_to_system(model: Model) -> Conjunction:
    """Construct a Conjunction representing the contents of a model."""
    system: Conjunction = []
    for t in sorted(model.keys()):
        symbol = t if model[t] else -1 * t
        system.append(set([symbol]))
    return system
