#!/usr/bin/env python3
import os
import argparse
import satsolver

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

    args = parser.parse_args()

    if args.strategy not in [1, 2, 3]:
        print(
            f"ERROR: provided strategy ({args.strategy}) must be an int in range [1,3]"
        )
        exit(1)

    if not os.path.isfile(args.inputfile):
        print(f"ERROR: input file not found '{args.inputfile}'")
        exit(1)

    print(f"running SAT with strategy {args.strategy} on file '{args.inputfile}'")

    # TODO:
    print("\nnot implemented yet!!!")
    exit(1)


if __name__ == "__main__":
    main()
