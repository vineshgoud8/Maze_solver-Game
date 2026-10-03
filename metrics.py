"""
metrics.py - Run algorithms fairly and collect measurable results.

FAIR COMPARISON RULES
  * every algorithm gets the SAME grid, SAME start and SAME goal
  * the algorithms never change the grid (each builds its own fresh data
    structures on every call, so no state is shared between runs)
  * timing runs do NOT record animation events (recording would slow things down)
  * timing uses time.perf_counter() and is averaged over several trials
"""

import time
import pandas as pd

from bfs import bfs
from dfs import dfs
from backtracking import backtracking

ALGORITHMS = {"BFS": bfs, "DFS": dfs, "Backtracking": backtracking}


def run_algorithm(name, grid, start, goal, trials=20):
    """Run one algorithm: once with events (for animation) + `trials` timing runs."""
    if name not in ALGORITHMS:
        raise ValueError(f"Unknown algorithm '{name}'.")
    trials = max(1, int(trials))
    func = ALGORITHMS[name]

    result = func(grid, start, goal, record_events=True)

    times_ms = []
    for _ in range(trials):
        t0 = time.perf_counter()
        func(grid, start, goal, record_events=False)
        times_ms.append((time.perf_counter() - t0) * 1000.0)

    result["time_ms"] = sum(times_ms) / len(times_ms)       # average
    result["time_min_ms"] = min(times_ms)
    result["time_max_ms"] = max(times_ms)
    result["trials"] = trials
    return result


def compare_all(grid, start, goal, trials=20):
    """Run BFS, DFS and Backtracking on the SAME maze."""
    return {name: run_algorithm(name, grid, start, goal, trials) for name in ALGORITHMS}


def format_time(ms):
    return f"{ms:.4f} ms"


def results_to_dataframe(results):
    rows = []
    for name, r in results.items():
        rows.append({
            "Algorithm": name,
            "Solution Found": "Yes" if r["found"] else "No",
            "Path Length (steps)": r["path_length"] if r["found"] else "-",
            "Visited Cells": r["visited_count"],
            "Backtracking Count": r["backtrack_count"] if name == "Backtracking" else "n/a",
            "Peak Queue/Stack/Depth": r["peak_size"],
            "Avg Time": format_time(r["time_ms"]),
        })
    return pd.DataFrame(rows)


def summary_notes(results):
    """Short factual sentences generated from the REAL measured numbers."""
    notes = []
    found = {n: r for n, r in results.items() if r["found"]}
    if not found:
        return ["No algorithm found a path: this maze has no solution."]
    shortest = min(r["path_length"] for r in found.values())
    for name, r in found.items():
        extra = r["path_length"] - shortest
        if extra == 0:
            notes.append(f"{name} found a path of {r['path_length']} steps (the shortest on this maze).")
        else:
            notes.append(f"{name} found a path of {r['path_length']} steps, {extra} longer than the shortest.")
    fewest = min(r["visited_count"] for r in results.values())
    leaders = [n for n, r in results.items() if r["visited_count"] == fewest]
    notes.append(f"Fewest visited cells on this maze: {', '.join(leaders)} ({fewest}).")
    notes.append("These numbers belong to THIS maze only; another maze can give a different ranking.")
    return notes
