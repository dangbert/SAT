#!/usr/bin/env python3
import os
import argparse
import copy
import logging
from satsolver import dimacs, dpll, puzzle, verify_model, model_to_system
from satsolver import strategy2, strategy3

# DIR = os.path.dirname(os.path.abspath(__file__))


def main():
    parser = argparse.ArgumentParser(
        description="General SAT solver which implements 3 different strategies"
    )

    parser.add_argument(
        "inputfile",
        type=str,
        help="file which contains all required rules followed by a puzzle (sudoku rules + given puzzle)",
    )
    parser.add_argument(
        "-S", "--strategy", type=int, default=1, help="which solving strategy to use"
    )
    parser.add_argument(
        "-d", "--debug", action="store_true", help="enable verbose debug logging"
    )
    parser.add_argument(
        "-i", "--input2", type=str, help="optional path to second input file"
    )
    parser.add_argument(
        "--sudoku",
        type=int,
        help="optionally specify size of sudoku board (for visualizing a sudoku solution)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="path to output path (defaults to <inputfile>.out)",
    )

    args = parser.parse_args()
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=log_level)

    outputfile = f"{os.path.basename(args.inputfile)}.out"
    if args.output:
        outputfile = args.output

    # parse input file
    if not os.path.isfile(args.inputfile):
        print(f"ERROR: input file not found '{args.inputfile}'")
        exit(1)
    if args.input2 and not os.path.isfile(args.input2):
        print(f"ERROR: input file not found '{args.input2}'")
        exit(1)

    print("parsing file...")
    system = dimacs.parse_file(args.inputfile)
    if args.input2:
        system += dimacs.parse_file(args.input2)

    orig_system = copy.deepcopy(system)
    model = {}
    print(f"running strategy {args.strategy} on system...\n")
    if args.strategy == 1:
        res, stats = dpll.solver(system, model)
    elif args.strategy == 2:
        res, stats = strategy2.solver(system, model)
    elif args.strategy == 3:
        res, stats = strategy3.solver(system, model)
    else:
        print(
            f"ERROR: provided strategy ({args.strategy}) must be an int in range [1,3]"
        )
        exit(1)

    print(f"stats = {stats}\n")
    if not res:
        print("system is inconsistent!")
        exit(0)

    if args.sudoku != None:
        print(puzzle.visualize_sudoku_model(model, board_size=args.sudoku))
    # sanity check (should always pass)
    valid, reason = verify_model(orig_system, model)
    if not valid:
        print(f"ERROR: solution was invalid! reason = {reason}")
        exit(1)

    print(f"found a valid solution!")
    with open(outputfile, "w") as f:
        f.write(dimacs.to_dimacs(model_to_system(model)))
    print(f"\nwrote result to '{outputfile}'")


if __name__ == "__main__":
    main()
