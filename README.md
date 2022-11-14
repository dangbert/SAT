# SAT Solver

This project implements a (general) [SAT solver](https://en.wikipedia.org/wiki/SAT_solver) which can be used to solve Sudoku problems.

This project uses the [DIMACS](https://logic.pdmi.ras.ru/~basolver/dimacs.html) file format.


## Usage:
````bash
./SAT.py [-h] [-S STRATEGY] inputfile

# example:
./SAT.py -S2 example_file.cnf

# you optioanlly use `-i` to read a second cnf file to be combined with the first:
#   (and optionally specify the output filename with `-o`)
./SAT.py -S1 rules/sudoku-rules-9x9.cnf -i example_sudokus/sudoku2.cnf -o out.cnf

# view full usage / help:
./SAT.py -h
````

## Strategies:

1. DPLL algorithm (without any further heuristics).

2. TODO

3. TODO

## Testing:

````bash
pip install pytest # (if needed)

# run all unit tests:
pytest

# run all tests (with extra debug logging):
pytest -s -o log_cli=true -o log_cli_level=DEBUG
````