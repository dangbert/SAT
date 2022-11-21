#!/usr/bin/env python3
"""Run an experiment, reporting stats about different strategies etc."""
import argparse
from collections.abc import Callable
import copy
import ctypes
from datetime import datetime
import json
import logging
import math
import matplotlib.pyplot as plt
from multiprocessing import Process, Array, Value, cpu_count, Manager
import os
import random
from satsolver import Conjunction, dimacs, puzzle, verify_model, Model, model_to_system
from satsolver import dpll, strategy2, strategy_random
import statistics
import subprocess
from tests.test_dpll import sudoku_tester
import time
from typing import List, Dict, Optional

SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))

RULES_4X4 = dimacs.parse_file(os.path.join(SCRIPT_DIR, "rules/sudoku-rules-4x4.cnf"))
RULES_9X9 = dimacs.parse_file(os.path.join(SCRIPT_DIR, "rules/sudoku-rules-9x9.cnf"))


# DIR = os.path.dirname(os.path.abspath(__file__))

FILES_9X9 = [
    "damnhard.sdk.txt",
    "top91.sdk.txt",
    "top95.sdk.txt",
    "top100.sdk.txt",
    "top870.sdk.txt",
    "1000 sudokus.txt",
    "top2365.sdk.txt",
]
FILES_9X9 = list(
    map(lambda fname: os.path.join(SCRIPT_DIR, "datasets", fname), FILES_9X9)
)

FILE_4X4 = os.path.join(SCRIPT_DIR, f"datasets/4x4.txt")


def main():
    parser = argparse.ArgumentParser(
        description="Runs and experiment, comparing different sat solver strategies."
    )

    parser.add_argument(
        "-c", "--count", type=int, help="max number of problems to run on"
    )
    parser.add_argument(
        "-m", "--message", type=str, help="description of experiment (to save)"
    )
    parser.add_argument(
        "--cpus", type=int, default="1", help="number of cpus (processes) to use"
    )
    parser.add_argument(
        "--shuffle", action="store_true", help="whether to shuffle dataset before using"
    )
    parser.add_argument("--seed", type=int, help="random seed to use")
    args = parser.parse_args()

    FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
    logging.basicConfig(format=FORMAT, level=logging.INFO)

    expname = datetime.now().strftime(f"%Y_%m_%d_%H_%M_%S")
    if args.message:
        msg = args.message.replace(" ", "_")[:25]
        expname += "--" + msg
    # expname = "tmp"  # TODO for now
    outdir = os.path.join("experiments/", expname)
    if not os.path.exists(outdir):
        logging.info(f"using dir: {outdir}")
        os.makedirs(outdir)

    args.cpus = min(args.cpus, cpu_count())

    # with open("stats.json", "r") as f:
    #    stats = json.load(f)
    # visualize_stats(stats, outdir)
    # exit(0)

    if args.seed is None:
        args.seed = random.randint(0, 9999)
    rng = random.Random()
    rng.seed(args.seed)
    logging.info(f"using random seed: {args.seed}")

    # visualize_stats(stats, outdir)
    # fnames = FILES_9X9[:1]
    fnames = FILES_9X9
    solvers = [
        dpll.solver,
        strategy2.solver,
        strategy_random.solver,
    ]
    outpath = os.path.join(outdir, "stats.json")
    MAX_PUZZLES = args.count
    logging.info(f"max_Puzzles = {MAX_PUZZLES}")
    stats = generic_experiment(
        RULES_9X9,
        fnames,
        solvers,
        args.cpus,
        max_puzzles=MAX_PUZZLES,
        outpath=outpath,
        shuffle=args.shuffle,
    )

    GIT_HASH = (
        subprocess.check_output(["git", "rev-parse", "--verify", "HEAD", "--short"])
        .decode("utf-8")
        .strip()
    )

    visualize_stats(stats, outdir)

    msg = args.message if args.message else ""
    with open(os.path.join(outdir, "about.txt"), "w") as f:
        f.write(
            f"{msg}\n\ncount={args.count}, seed={args.seed}\nshuffle={args.shuffle == True}\n{GIT_HASH}\n"
        )

    # all_9x9()
    exit(0)

    rules = dimacs.parse_file(RULES_9X9)

    # sudoku = "1.3....44....3.1"

    # TODO:

    # rules = dimacs.parse_file(RULES_4X4)
    system = puzzle.encode_puzzle(sudoku) + rules

    model: Model = {}
    res, stats = dpll.solver(system, model)
    valid, reason = verify_model(system, model)
    import pdb

    pdb.set_trace()

    assert res and valid
    grid = puzzle.visualize_sudoku_model(model, 4)
    print(grid)

    solution = model_to_system(model)
    print()
    print(solution)


def all_9x9():
    """Verify dpll can solve set of 9x9 examples."""
    fnames = [
        "damnhard.sdk.txt",
        # "top91.sdk.txt",
        # "top95.sdk.txt",
        # "top100.sdk.txt",
        # "top870.sdk.txt",
        # "1000 sudokus.txt",
        # "top2365.sdk.txt",
    ]
    for fname in fnames:
        print("running on file: " + fname)
        fname = os.path.join(SCRIPT_DIR, "datasets", fname)
        sudoku_tester(RULES_9X9, fname, 9, report_stats=True)


def generic_experiment(
    rules: Conjunction,
    fnames: List[str],
    solvers: List[Callable],
    cpus: int,  # number of processes to use
    max_puzzles: Optional[int] = None,
    outpath: Optional[str] = None,
    shuffle: Optional[bool] = False,
) -> Dict:
    # gather list of puzzle (systems) across files
    all_puzzles = []
    for fname in fnames:
        with open(fname, "r") as f:
            for line in f.readlines():
                if not line:
                    continue
                line = line.replace("\n", "")
                all_puzzles.append(puzzle.encode_puzzle(line))

    if shuffle:
        logging.info("shuffling puzzles")
        random.shuffle(all_puzzles)
    if max_puzzles is not None:
        logging.info(f"limiting to {max_puzzles} puzzles (of {len(all_puzzles)} total)")
        all_puzzles = all_puzzles[:max_puzzles]

    all_stats: List[Dict] = []
    # all_stats = Array(Dict, range(len(solvers)))

    STATS_TEMPLATE = {
        "cpu_times": [],  # time per puzzle
        "outcome": [],  # result of puzzle solve (True if solved else False)
        "backtracks": [],  # backtracks per puzzle
    }
    for i in range(len(solvers)):
        logging.info(f"\n*** solver {i+1}/{len(solvers)} starting... ***")

        # https://superfastpython.com/multiprocessing-manager-example/
        with Manager() as manager:
            # process-safe shared list:
            flat_stats = manager.list(
                [copy.deepcopy(STATS_TEMPLATE) for _ in range(cpus)]
            )

            solver = solvers[i]
            systems = copy.deepcopy([system + rules for system in all_puzzles])

            next_index = 0
            bin_size = math.ceil(len(systems) / cpus)
            plist: List[Process] = []
            for c in range(cpus):
                stop_index = min(next_index + bin_size, len(systems))
                worker_systems = systems[next_index:stop_index]
                logging.info(
                    f"starting worker {c+1}/{cpus} with {len(worker_systems)} problems ({next_index}:{stop_index})"
                )
                next_index += bin_size

                plist.append(
                    Process(
                        target=_worker,
                        args=(
                            solver,
                            worker_systems,
                            flat_stats,
                            c,
                        ),
                    )
                )
                plist[-1].start()

            logging.info("awaiting workers...")
            for p in plist:
                p.join()
            logging.info("all workers done!")

            # flatten worker stats into single dict
            joined_stats = {}
            for s in flat_stats:
                for key in STATS_TEMPLATE.keys():
                    if key not in joined_stats:
                        joined_stats[key] = []
                    joined_stats[key] += s[key]
            all_stats.append(joined_stats)

            # print("\n" + "".join(["_" for _ in range(board_size * 2)]))
            # print(puzzle.visualize_sudoku_model(model, board_size=board_size))
        logging.info(f"\n^^^ solver {i+1}/{len(solvers)} done. ^^^")

    if outpath is not None:
        with open(outpath, "w") as f:
            json.dump(all_stats, f, indent=2)  # write indented json to file
            logging.info(f"wrote stats to: {os.path.abspath(outpath)}")
    return all_stats


def _worker(solver: Callable, systems: List[Conjunction], arr: Array, ai: int):
    """Solve given systems and and update stats in arr[ai]."""

    cur_stats = arr[ai]
    for p, system in enumerate(systems):
        model: Model = {}
        # https://docs.python.org/3/library/time.html#time.process_time
        if p % max(10, math.floor(len(systems) / 20)) == 0:
            logging.info(f"at puzzle {p+1}/{len(systems)}")
        cpu_time = time.process_time()
        res, stats = solver(system, model)
        cpu_time = time.process_time() - cpu_time

        cur_stats["cpu_times"].append(cpu_time)
        cur_stats["backtracks"].append(stats["backtracks"])

        valid, reason = verify_model(system, model)
        # assert valid
        cur_stats["outcome"].append(res and valid)

    arr[ai] = cur_stats
    logging.info("worker done!")


def visualize_stats(stats: Dict, outdir: str):
    logging.info(f"processing stats...\n")

    keys = ["cpu_times", "backtracks"]
    num_solvers = len(stats)
    plt.clf()
    fig, axis = plt.subplots(num_solvers, len(keys))
    fig.tight_layout(h_pad=4)
    plt.gcf().set_size_inches(11, 8.5)

    for i, ss in enumerate(stats):
        print(f"\nsolver {i+1}/{len(stats)}:")
        # solver stats
        avg = 0.0

        assert False not in ss["outcome"]

        for k, key in enumerate(keys):
            avg = sum(ss[key]) / len(ss[key])
            stdev = statistics.stdev(ss[key])
            sample_length = len(ss[key])

            print(f"avg {key}: {avg:.3f}")

            splot = axis[i][k]
            splot.set_xlabel(f"{key} (n={sample_length})")
            splot.set_ylabel(f"count")
            # splot.set_ylabel(f"voltage (mV?)")
            splot.set_title(f"solver {i+1}: {key} (avg={avg:.3f}, stdev={stdev:.3f})")
            # TODO: ensure same bin sizes / axis ranges for all solver's historgrams (for this key)
            # or use dot/frequency plot...
            splot.hist(ss[key], bins=10)

    graph_out = os.path.join(outdir, f"graphs.pdf")
    plt.savefig(graph_out, dpi=400)
    print(f"wrote: {graph_out}")


if __name__ == "__main__":
    main()
