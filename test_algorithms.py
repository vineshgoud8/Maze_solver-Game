"""
test_algorithms.py - Automated tests.  Run with:   python test_algorithms.py
(or `pytest` if you have it installed).
"""

from maze import generate_maze, parse_maze, is_valid_path, is_solvable
from metrics import ALGORITHMS, run_algorithm, compare_all
from visualization import build_state

SOLVABLE = """
S.#..
.##.#
...#.
.#...
...#G
"""
UNSOLVABLE = """
S.#..
..#..
###..
...#G
....."""


def test_all_find_valid_path_on_solvable_maze():
    grid, s, g = parse_maze(SOLVABLE)
    for name, func in ALGORITHMS.items():
        r = func(grid, s, g)
        assert r["found"], name
        assert is_valid_path(grid, r["path"], s, g), name


def test_unsolvable_maze_handled():
    grid, s, g = parse_maze(UNSOLVABLE)
    for name, func in ALGORITHMS.items():
        r = func(grid, s, g)
        assert not r["found"] and r["path"] == [] and r["path_length"] is None, name
        assert r["events"][-1]["type"] == "no_path", name
    assert not is_solvable(grid, s, g)


def test_smallest_mazes():
    grid, s, g = parse_maze("SG.\n...\n...")          # goal right next to the start
    for name, func in ALGORITHMS.items():
        assert func(grid, s, g)["path_length"] == 1, name
    grid, s, g = parse_maze("S#G\n###\n...")          # walled in
    for name, func in ALGORITHMS.items():
        assert not func(grid, s, g)["found"], name


def _true_shortest(grid, s, g):
    """Independent check: repeated relaxation (Bellman-Ford style), not a queue."""
    INF = 10 ** 9
    dist = {(r, c): INF for r, row in enumerate(grid) for c, ch in enumerate(row) if ch != "#"}
    dist[s] = 0
    changed = True
    while changed:
        changed = False
        for (r, c), d in list(dist.items()):
            if d == INF:
                continue
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nb = (r + dr, c + dc)
                if nb in dist and dist[nb] > d + 1:
                    dist[nb] = d + 1
                    changed = True
    return dist[g]


def test_bfs_is_shortest_and_dfs_is_not_shorter():
    for seed in range(15):
        for diff in ("Easy", "Medium", "Hard"):
            grid, s, g = generate_maze(15, diff, seed)
            res = compare_all(grid, s, g, trials=1)
            best = _true_shortest(grid, s, g)
            assert res["BFS"]["path_length"] == best
            assert res["DFS"]["path_length"] >= best
            assert res["Backtracking"]["path_length"] >= best


def test_generated_mazes_are_solvable():
    for size in (7, 15, 25, 41):
        for diff in ("Easy", "Medium", "Hard"):
            grid, s, g = generate_maze(size, diff, seed=size)
            assert is_solvable(grid, s, g)


def test_backtracking_counts_undo_operations():
    grid, s, g = generate_maze(21, "Medium", seed=3)
    r = run_algorithm("Backtracking", grid, s, g, trials=1)
    # every visited cell that is NOT on the final path was undone exactly once
    assert r["backtrack_count"] == r["visited_count"] - len(r["path"])
    assert sum(e["type"] == "backtrack" for e in r["events"]) == r["backtrack_count"]


def test_replay_ends_with_final_path():
    grid, s, g = generate_maze(15, "Medium", seed=5)
    for name in ALGORITHMS:
        r = run_algorithm(name, grid, s, g, trials=1)
        state = build_state(r["events"], len(r["events"]))
        assert state["final_path"] == r["path"]


def test_grid_not_modified():
    grid, s, g = generate_maze(15, "Easy", seed=9)
    before = [row[:] for row in grid]
    compare_all(grid, s, g, trials=2)
    assert grid == before


def test_invalid_maze_text():
    for bad in ("", "S.\n..", "S.G\n..", "S.G\n.X.\n...", "SSG\n...\n...", "...\n...\n..."):
        try:
            parse_maze(bad)
        except ValueError:
            continue
        raise AssertionError(f"should have been rejected: {bad!r}")


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print("PASS", t.__name__)
    print(f"\nAll {len(tests)} tests passed.")
