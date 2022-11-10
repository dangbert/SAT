from satsolver import Conjunction, Disjunction
from satsolver import dimacs


def test_simple_parse():
    """Test parsing of a simple dimacs file."""
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

    res = dimacs.parse_string(contents)
    assert res == expected


def test_to_dimacs():
    """Test serializing a logic system to a string."""
    system: Disjunction = [
        set([111, 112, 113]),
        set([-111, -112]),
    ]
    res = dimacs.to_dimacs(system)
    expected = "p cnf 3 2\n111 112 113 0\n-111 -112 0\n"
    assert res == expected


def test_bidirectional_encoding():
    """Test we can encode/decode from dimacs string <-> Disjunction."""
    content = "p cnf 3 2\n111 112 113 0\n-111 -112 0\n"
    system = dimacs.parse_string(content)
    res = dimacs.to_dimacs(system)
    assert content == res
