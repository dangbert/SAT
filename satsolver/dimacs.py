import os
from satsolver import Conjunction


def parse_string(contents: str) -> Conjunction:
    """Convert a DIMACS string (with newlines) to a Disjunction."""

    res: Conjunction = []
    for line in contents.split("\n"):
        line = line.strip()  # ignore extra whitespace
        if not line:  # blank line
            continue
        tokens = line.split(" ")
        if tokens[0] == "c":
            continue  # ignore comments
        if tokens[0] == "p":
            continue  # ignore this line for now
        tokens = [t for t in tokens if t != ""]

        try:
            tokens = [int(t) for t in tokens]
            assert tokens[-1] == 0
            tokens = tokens[:-1]  # throw away 0 at end
        except ValueError as e:
            print(f"ERROR parsing line: '{line}'")
            raise e
        if 0 in tokens:
            raise ValueError(f"0 shouldn't appear prior to the end of a line: '{line}'")
        res.append(set(tokens))

    return res


def parse_file(fname: str) -> Conjunction:
    """Parse a .cnf file and return a conjunction."""
    assert os.path.exists(fname)
    with open(fname, "r") as f:
        lines = [line for line in f.readlines()]
    return parse_string("".join(lines))


def to_dimacs(system: Conjunction) -> str:
    """Convert a logic system to a (newline delimited) DIMACS string."""
    content = ""
    vars = set()
    for clause in system:
        vars = vars.union(set([abs(t) for t in clause]))
        # sort tokens by absolute value (increasing)
        str_tokens = [str(t) for t in sorted(list(clause), key=lambda v: abs(v))]
        content += " ".join(str_tokens) + " 0\n"

    content = f"p cnf {len(vars)} {len(system)}\n" + content
    return content
