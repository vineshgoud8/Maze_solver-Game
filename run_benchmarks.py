"""
run_benchmarks.py - Print real measurements for the report / slides.

    python run_benchmarks.py

Path length, visited cells and backtracking count are the same on every computer for
the same seed.  Time depends on YOUR computer, so copy the times from your own run.
"""

from maze import generate_maze
from metrics import compare_all

CASES = [("Small", 11, "Medium", 1), ("Medium", 21, "Medium", 1), ("Large", 41, "Medium", 1),
         ("Medium-Easy", 21, "Easy", 1), ("Medium-Hard", 21, "Hard", 1)]
TRIALS = 50

print(f"{'Case':<12}{'Size':<7}{'Diff':<8}{'Algorithm':<14}{'Path':<6}{'Visited':<9}{'Backtracks':<11}{'Avg ms':<10}")
print("-" * 77)
for label, size, diff, seed in CASES:
    grid, s, g = generate_maze(size, diff, seed)
    for name, r in compare_all(grid, s, g, TRIALS).items():
        bt = r["backtrack_count"] if name == "Backtracking" else "n/a"
        print(f"{label:<12}{size:<7}{diff:<8}{name:<14}{r['path_length']!s:<6}{r['visited_count']:<9}{bt!s:<11}{r['time_ms']:<10.4f}")
