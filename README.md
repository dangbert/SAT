# SAT Solver

This project implements a (general) [SAT solver](https://en.wikipedia.org/wiki/SAT_solver) which can be used to solve Sudoku problems.

This project uses the [DIMACS](https://logic.pdmi.ras.ru/~basolver/dimacs.html) file format.


## Usage:
````bash
./SAT.py [-h] [-S STRATEGY] inputfile

# example:
./SAT.py -S2 sudoku_nr_10

# view full usage / help:
./SAT.py -h
````

## Strategies:

1. DPLL algorithm (without any further heuristics).

2. TODO

3. TODO