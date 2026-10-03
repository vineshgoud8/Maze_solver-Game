"""
backtracking.py - Recursive Backtracking

IDEA:  CHOOSE a cell  ->  EXPLORE from it  ->  if it is a DEAD END, UNDO the choice
and try the next option.

We keep a list called `path` = the cells of the route we are currently building.
  * choose   : add the cell to `path`
  * explore  : recursively try its neighbours
  * undo     : if every neighbour failed, REMOVE the cell from `path` (backtrack)

Note: we remember cells we have already tried (`visited`) so we never walk in
circles or repeat hopeless work.  Because of that, on a grid maze this search
visits cells in the same order as DFS - the difference is that Backtracking keeps
(and visibly UNDOES) a current path, and we count every undo operation.
"""

import sys
from maze import make_event, neighbors, make_result


def backtracking(grid, start, goal, record_events=True):
    visited = set()          # cells already tried
    path = []                # the route being built right now
    visit_order = []
    events = []
    stats = {"backtracks": 0, "peak": 0}

    # Recursion needs enough "depth" for long corridors (one level per cell).
    old_limit = sys.getrecursionlimit()
    sys.setrecursionlimit(max(old_limit, len(grid) * len(grid[0]) + 1000))

    def solve(cell):
        # ---- CHOOSE ----
        visited.add(cell)
        visit_order.append(cell)
        path.append(cell)
        stats["peak"] = max(stats["peak"], len(path))
        if record_events:
            events.append(make_event("choose", cell, f"CHOOSE {cell}: add it to the current path"))

        if cell == goal:                        # base case: success
            if record_events:
                events.append(make_event("goal", cell, "Goal reached!"))
            return True

        # ---- EXPLORE ----
        tried_any = False
        for nb in neighbors(grid, cell):
            if nb in visited:                   # skip cells we already tried
                continue
            tried_any = True
            if record_events:
                events.append(make_event("explore", nb, f"EXPLORE: try {nb} from {cell}"))
            if solve(nb):                       # recursive call
                return True

        # ---- DEAD END -> UNDO ----
        if record_events:
            why = "every option failed" if tried_any else "no unvisited neighbours"
            events.append(make_event("dead_end", cell, f"DEAD END at {cell} ({why})"))
        path.pop()                              # undo the choice
        stats["backtracks"] += 1
        if record_events:
            events.append(make_event("backtrack", cell, f"UNDO {cell}: remove it from the path and go back"))
        return False

    try:
        found = solve(start)
    finally:
        sys.setrecursionlimit(old_limit)

    if found:
        final_path = list(path)
        if record_events:
            events.append(make_event(
                "path", goal, f"Path found: {len(final_path) - 1} steps; {stats['backtracks']} undo operations",
                path=final_path))
        return make_result("Backtracking", True, final_path, visit_order, events,
                           stats["backtracks"], stats["peak"])

    if record_events:
        events.append(make_event("no_path", start, "Every choice was undone: there is no path to the goal"))
    return make_result("Backtracking", False, [], visit_order, events,
                       stats["backtracks"], stats["peak"])
