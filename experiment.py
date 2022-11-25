#!/usr/bin/env python3
"""Run an experiment, reporting stats about different strategies etc."""
import argparse
from collections.abc import Callable
import copy
import csv
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
from satsolver import dpll, strategy2, strategy3, strategy_random, strategy_template
import statistics
import subprocess
from tests.test_dpll import sudoku_tester
import time
from typing import List, Dict, Optional, Tuple

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
        "-r",
        "--replay",
        type=str,
        help="folder to reprocess stats.json (instead of running new experiment).",
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

    if args.replay:
        fname = os.path.abspath(args.replay)
        if not fname.endswith(".json"):
            fname = os.path.join(fname, "stats.json")
        outdir = os.path.dirname(fname)
        assert os.path.isdir(outdir) and os.path.exists(fname)

        with open(fname, "r") as f:
            stats = json.load(f)
        logging.info(f"replaying stat visualization of: '{fname}'")
        visualize_stats(stats, outdir)
        exit(0)

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

    if args.seed is None:
        args.seed = random.randint(0, 9999)
    rng = random.Random()
    rng.seed(args.seed)
    logging.info(f"using random seed: {args.seed}")

    """
    solvers = [
        (strategy2.solver, "strategy2"),
        (dpll.solver, "base algo"),
        # (strategy3.solver, "strategy3"),
        # (strategy_random.solver, "random splitting"),
    ]
    """
    solvers = get_purity_solvers()

    fnames = FILES_9X9
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


def get_purity_solvers():
    """Get 4 varations of purity selection for comparision."""
    return [
        (strategy2.solver, "lowest_purity"),
        (
            strategy_template.strategy_template(
                strategy_template.simplify, strategy2.select_lowest_purity__reversed
            ),
            "lowest_purity__reversed",
        ),
        (
            strategy_template.strategy_template(
                strategy_template.simplify,
                strategy2.select_highest_purity,
            ),
            "highest_purity",
        ),
        (
            strategy_template.strategy_template(
                strategy_template.simplify,
                strategy2.select_highest_purity__reversed,
            ),
            "highest_purity__reversed",
        ),
    ]


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
    solvers: List[Tuple[Callable, str]],
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

    STATS_TEMPLATE = {
        "cpu_times": [],  # time per puzzle
        "outcome": [],  # result of puzzle solve (True if solved else False)
        "backtracks": [],  # backtracks per puzzle
    }

    def write_stats():
        nonlocal outpath
        nonlocal all_stats
        if outpath is not None:
            with open(outpath, "w") as f:
                json.dump(all_stats, f, indent=2)  # write indented json to file
                logging.info(f"wrote latest stats to: {os.path.abspath(outpath)}")

    for i in range(len(solvers)):
        logging.info(f"\n*** solver {i+1}/{len(solvers)} starting... ***")

        solver, desc = solvers[i]
        systems = copy.deepcopy([system + rules for system in all_puzzles])
        if cpus == 1:
            # (skip extra overhead of using multiprocessing)
            all_stats.append(copy.deepcopy(STATS_TEMPLATE))
            all_stats[-1]["desc"] = desc
            _worker(
                solver, systems, all_stats, len(all_stats) - 1, write_stats=write_stats
            )
            logging.info(f"\n^^^ solver {i+1}/{len(solvers)} done. ^^^")
            write_stats()
            continue

        # https://superfastpython.com/multiprocessing-manager-example/
        with Manager() as manager:
            # process-safe shared list:
            flat_stats = manager.list(
                [copy.deepcopy(STATS_TEMPLATE) for _ in range(cpus)]
            )

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
            write_stats()

            # flatten worker stats into single dict
            joined_stats = {"desc": desc}
            for s in flat_stats:
                for key in STATS_TEMPLATE.keys():
                    if key not in joined_stats:
                        joined_stats[key] = []
                    joined_stats[key] += s[key]
            all_stats.append(joined_stats)

            # print("\n" + "".join(["_" for _ in range(board_size * 2)]))
            # print(puzzle.visualize_sudoku_model(model, board_size=board_size))
        logging.info(f"\n^^^ solver {i+1}/{len(solvers)} done. ^^^")

    write_stats()
    return all_stats


def _worker(
    solver: Callable,
    systems: List[Conjunction],
    arr: Array,
    ai: int,
    write_stats: Optional[Callable] = None,
):
    """Solve given systems and and update stats in arr[ai]."""

    cur_stats = arr[ai]
    for p, system in enumerate(systems):
        model: Model = {}
        # https://docs.python.org/3/library/time.html#time.process_time
        if p % max(10, math.floor(len(systems) / 20)) == 0:
            logging.info(f"at puzzle {p+1}/{len(systems)}")
            if write_stats is not None:
                write_stats()  # just to help track progress
        cpu_time = time.process_time()
        orig_system = copy.deepcopy(system)
        res, stats = solver(system, model)
        cpu_time = time.process_time() - cpu_time

        cur_stats["cpu_times"].append(cpu_time)
        cur_stats["backtracks"].append(stats["backtracks"])

        valid, reason = verify_model(orig_system, model)
        # assert valid
        cur_stats["outcome"].append(int(res and valid))

    arr[ai] = cur_stats
    logging.info("worker done!")


# https://matplotlib.org/stable/gallery/statistics/boxplot_demo.html#boxplots
def visualize_stats(stats: Dict, outdir: str):
    logging.info(f"processing stats...\n")

    num_solvers = len(stats)
    plt.clf()
    # fig, ax1 = plt.subplots(num_rows, len(keys))
    # fig, axis = plt.subplots(num_solvers, len(keys))
    # fig.tight_layout(h_pad=4)
    # plt.gcf().set_size_inches(11, 8.5)

    keys = ["cpu_times", "backtracks"]
    var = "backtracks"  # measured variable to plot
    # var = "cpu_times"
    var_title = "Backtracks"
    # var_title = "CPU Time (sec)"
    sample_lengths = []

    for i, ss in enumerate(stats):
        desc = "" if "desc" not in ss else ss["desc"]
        if desc:
            print(f"\nsolver {i+1}/{len(stats)} ({desc}):")
        else:
            print(f"\nsolver {i+1}/{len(stats)}:")
        # solver stats
        avg = 0.0

        if isinstance(ss["outcome"], list):
            assert 0 not in ss["outcome"], "ensure all solves successful"

        for k, key in enumerate(keys):
            avg = sum(ss[key]) / len(ss[key])
            stdev = statistics.stdev(ss[key])
            sample_length = len(ss[key])
            median = statistics.median(ss[key])

            print(f"median {key}:\t{median:.3f}")
            print(f"avg {key}:\t{avg:.3f}")
            print(f"stdev {key}:\t{stdev:.3f}")
            print(f"sample_length {key}:\t{sample_length}\n")
            sample_lengths.append(sample_length)

    data = [ss[var] for ss in stats]
    descs = [
        ss["desc"] if "desc" in ss else f"Solver {i+1}" for i, ss in enumerate(stats)
    ]

    csv_out = os.path.join(outdir, f"stats.csv")
    with open(csv_out, "w") as f:
        writer = csv.writer(f)
        writer.writerow([f"{desc} {var}" for desc in descs])

        for n in range(max(sample_lengths)):
            row_data = []
            for s_idx in range(num_solvers):
                val = ""
                try:
                    val = data[s_idx][n]
                except IndexError as e:
                    pass  # in case this solver's dataset has a lower sample_length
                row_data.append(val)
            writer.writerow(row_data)
    print(f"\nwrote: {csv_out}")

    fig, axs = plt.subplots(2, len(data))
    fig.set_size_inches((11, 8.5))

    if len(data) > 3:
        fig.set_size_inches((11 * 1.25, 8.5 * 1.24))
    fig.tight_layout(pad=6.0)

    ymax = max([max(d) for d in data])  # includes outliers
    ymin = 0
    ymax_no_outliers = 0

    for i in range(len(data)):
        d, desc = data[i], descs[i]
        ax = axs[0, i] if len(data) > 1 else axs[0]
        ax.boxplot(d)
        ax.set_title(desc)
        ax.set_ylabel(var_title)
        ax.set_ylim([ymin, ymax])
        # ax.get_xaxis().set_visible(False)
        ax.set_xticks([])  # don't show any ticks/values on x axis
        ax.set_xlabel(f"({chr(ord('a') + i)})", fontsize=14, fontweight="bold")

        # ax.text( 0.0, 0.00, "(a)", multialignment="center", # ha="center", fontsize=12, bbox={"facecolor": "orange", "alpha": 0.5, "pad": 5})

        ax = axs[1, i] if len(data) > 1 else axs[1]
        ax.boxplot(d, 0, "")
        ax.set_title(f"{desc}\n(omitting outliers)")
        ax.set_ylabel(var_title)
        # ax.get_xaxis().set_visible(False)
        ax.set_xticks([])  # don't show any ticks/values on x axis
        ax.set_xlabel(
            f"({chr(ord('a') + len(data) + i)})", fontsize=14, fontweight="bold"
        )
        ymax_no_outliers = max(math.ceil(ax.get_ylim()[1]), ymax_no_outliers)

    """
    # for manually adjusting scales of a subset of axs:
    ymax_override_top = max(
        math.ceil(axs[0, 0].get_ylim()[1]),
        math.ceil(axs[0, 1].get_ylim()[1]),
        math.ceil(axs[0, 2].get_ylim()[1]),
    )
    ymax_override_bottom = max(
        math.ceil(axs[1, 0].get_ylim()[1]),
        math.ceil(axs[1, 0].get_ylim()[1]),
        math.ceil(axs[1, 2].get_ylim()[1]),
    )
    print(f"ymax override top, bottom = {ymax_override_top}, {ymax_override_bottom}")
    """

    # ensure same bounds across bottom row of graphs
    for i in range(len(data)):
        ax = axs[1, i] if len(data) > 1 else axs[1]
        ax.set_ylim([ymin, ymax_no_outliers])

    # for "compare vs random" backtracks:
    """
    axs[0, 0].set_ylim([ymin, 4609])
    axs[0, 1].set_ylim([ymin, 4609])
    axs[0, 2].set_ylim([ymin, 4609])
    axs[1, 0].set_ylim([ymin, 122])
    axs[1, 1].set_ylim([ymin, 122])
    axs[1, 2].set_ylim([ymin, 122])
    """

    # for "compare vs random" cpu_times:
    """
    axs[0, 0].set_ylim([ymin, 280])
    axs[0, 1].set_ylim([ymin, 280])
    axs[0, 2].set_ylim([ymin, 280])
    axs[1, 0].set_ylim([ymin, 3])
    axs[1, 1].set_ylim([ymin, 3])
    axs[1, 2].set_ylim([ymin, 3])
    """

    # for 4purities backtracks:
    """
    axs[0, 0].set_ylim([ymin, 75])
    axs[0, 1].set_ylim([ymin, 75])
    axs[1, 0].set_ylim([ymin, 33])
    axs[1, 1].set_ylim([ymin, 33])
    """

    # for 4purities cpu_times:
    """
    axs[0, 0].set_ylim([ymin, 3])
    axs[0, 1].set_ylim([ymin, 3])
    axs[1, 0].set_ylim([ymin, 1])
    axs[1, 1].set_ylim([ymin, 1])
    """

    # bp = axs.boxplot(data, notch="True")

    # ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
    # axs.set_xticklabels(descs, rotation=45)
    # axs.get_xaxis().tick_bottom()
    # axs.get_yaxis().tick_left()

    # plt.title(f"{var_title} of {len(stats)} Solvers")

    graph_out = os.path.join(outdir, f"graphs_{var}.pdf")
    # if os.path.exists(graph_out):
    #    graph_out = os.path.join(outdir, f"graphs_new.pdf")
    plt.savefig(graph_out, dpi=400)
    print(f"wrote: {graph_out}")


if __name__ == "__main__":
    main()
