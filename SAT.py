#!/usr/bin/env python3
import os
import argparse
import logging
from satsolver import dimacs, dpll

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

    args = parser.parse_args()
    if args.strategy not in [1, 2, 3]:
        print(
            f"ERROR: provided strategy ({args.strategy}) must be an int in range [1,3]"
        )
        exit(1)
    log_level = args.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=log_level)

    # parse input file
    if not os.path.isfile(args.inputfile):
        print(f"ERROR: input file not found '{args.inputfile}'")
        exit(1)
    if args.input2 and not os.path.isfile(args.input2):
        print(f"ERROR: input file not found '{args.input2}'")
        exit(1)

    with open(args.inputfile, "r") as f:
        lines = [line for line in f.readlines()]
    if args.input2:
        with open(args.input2, "r") as f:
            lines += [line for line in f.readlines()]

    print("parsing file...")
    system = dimacs.parse_string("".join(lines))

    print(f"running strategy {args.strategy} on system...\n")
    if args.strategy == 1:
        model = {}
        res = dpll.dpll(system, model)
    else:
        # TODO:
        print("\nnot implemented yet!!!")
        exit(1)

    if not res:
        print("system is inconsistent!")
        exit(0)

    # TODO: verify final model includes all vars!
    outputfile = f"{os.path.basename(args.inputfile)}.out"
    with open(outputfile, "w") as f:
        f.write(dimacs.to_dimacs(system))
    print(f"\nwrote result to '{outputfile}'")

    # print(f"final model")
    # print(model)
    # TODO: write model somewhere?


if __name__ == "__main__":
    main()
