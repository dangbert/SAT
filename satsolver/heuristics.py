from collections import defaultdict

def dlis(system):
    """
    Implements DLIS (Dynamic Largest Individual Sum) heuristic.
    Returns the variable, positive or negative, that satifies the max nbr of unsatisfied clauses.
    """
    # assign a count to all literals (default 0)
    count = defaultdict(int)

    for clause in system:

        # increase count
        for t in clause:
            count[t] += 1

    # determine literal with max occurrence
    return max(count, key=count.get)
