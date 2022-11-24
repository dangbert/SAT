# SAT Solver

This project implements a (general) [SAT solver](https://en.wikipedia.org/wiki/SAT_solver) which can be used to solve SAT problems such as Sudoku.

This project uses the [DIMACS](https://logic.pdmi.ras.ru/~basolver/dimacs.html) file format to read and output SAT logic systems.

## Usage:
Note: the commands below reference `./SAT.py`, but for convenience we've also included the binary file `./SAT` which can be run with the same flags specified below.  `./SAT` is a portable binary created using [pyinstaller](https://pyinstaller.org/en/stable/). If you have any troubles running it for any reason then please run `./SAT.py` instead (which requires python3 to be installed).


````bash
# simple usage:
./SAT.py inputfile [-S STRATEGY] [-i INPUT2]

# example (outputs to example_file.cnf.out):
./SAT.py -S2 example_file.cnf

# you optioanlly use `-i` to read a second cnf file to be combined with the first:
#   (and optionally specify the output filename with `-o`)
./SAT.py -S1 rules/sudoku-rules-9x9.cnf -i example_sudokus/sudoku2.cnf -o out.cnf

# if solving a sudoku problem, you can optionally use `--sudoku [int]` to specify the board size (for visualizing the result)
./SAT.py -S3 rules/sudoku-rules-9x9.cnf -i example_sudokus/sudoku4.cnf  -o out.cnf --sudoku 9

# view full usage / help:
./SAT.py -h
````

## Setup:
Setting up a virtualenv / installing dependencies is generally not needed to run `SAT.py`, but to run `experiment.py` you will need to install some dependencies as explained below:

````bash
pip install virtualenv

# create virtual environment for this repo:
virtualenv .venv
. .venv/bin/activate
pip install -r requirements.txt

# now you can run experiment.py (see experiments section of this document)!
````

Note: this repo was developed/tested using python 3.8.10


## Strategies:
Supported strategies that can be selected with the `-S [int]` flag when running SAT.py:

1. DPLL algorithm (without any further heuristics).

2. "Purity selection": the variable with the lowest purity is selected to split on (see paper).

3. DLIS

## Testing:

````bash
pip install pytest # (if needed)

# run all unit tests:
pytest

# run all unit tests (with extra debug logging):
pytest -s -o log_cli=true -o log_cli_level=DEBUG
````

## Running experiments:
You can run `./experiment.py` to run an experiment comparing several algorithms on the 9x9 sudoku dataset.  Manually update the `solvers` list in the file if you want to customize which algorithms are tested.

````bash
# see full usage/help
./experiment.py -h

# example usage:
#  (comparing algorithms across 100 randomly sampled sudoku problems)
./experiment.py -m "my cool experiment" --shuffle --count 100
````