from satsolver import Conjunction, Disjunction


def parse_string(contents: str) -> Disjunction:
    """convert a DIMACS string (with newlines) to a Disjunction."""

    res: Disjunction = []
    for line in contents.split("\n"):
        line = line.strip()  # ignore extra whitespace
        if not line:  # blank line
            continue
        tokens = line.split(" ")
        if tokens[0] == "p":
            continue  # ignore this line for now
        tokens = tokens[:-1]  # throw away 0 at end

        tokens = [int(t) for t in tokens]
        res.append(set(tokens))

    return res
