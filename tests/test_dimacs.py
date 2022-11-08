from satsolver import Conjunction, Disjunction
from satsolver.dimacs import parse_string


def test_simple_parse():
    """ "test parsing of a simple dimacs file."""
    contents = """
        p cnf 444 448
        111 112 113 114 0
        -111 -112 0
        -111 -113 0
    """

    expected = [
        set([111, 112, 113, 114]),
        set([-111, -112]),
        set([-111, -113]),
    ]

    res = parse_string(contents)

    assert res == expected
