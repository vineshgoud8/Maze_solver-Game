"""
dfs.py - Depth-First Search (DFS)

IDEA: go as DEEP as possible along one corridor.  Only when we get stuck do we jump
back and try another branch.  A STACK (last in, first out) does this naturally:
the cell we added most recently is the next one we explore.

DFS finds A path (if one exists) but NOT necessarily the shortest one.
"""

from maze import make_event, neighbors, reconstruct_path, make_result


def dfs(grid, start, goal, record_events=True):
    stack = [(start, None)]         # (cell, the cell we came from)
    visited = set()
    parent = {}
    visit_order = []
    events = []
    peak = 1

    while stack:
        cell, came_from = stack.pop()           # take from the TOP of the stack
        if cell in visited:                     # may be pushed twice; skip repeats
            continue
        visited.add(cell)
        parent[cell] = came_from
        visit_order.append(cell)
        if record_events:
            events.append(make_event("visit", cell, f"Go deeper: explore {cell} (top of stack)"))

        if cell == goal:
            path = reconstruct_path(parent, goal)
            if record_events:
                events.append(make_event("goal", cell, "Goal reached!"))
                events.append(make_event(
                    "path", cell,
                    f"A path was found: {len(path) - 1} steps (not guaranteed shortest)", path=path))
            return make_result("DFS", True, path, visit_order, events, 0, peak)

        pushed = 0
        # Push neighbours in reverse so the FIRST direction is explored first.
        for nb in reversed(neighbors(grid, cell)):
            if nb not in visited:
                stack.append((nb, cell))
                pushed += 1
                if record_events:
                    events.append(make_event("explore", nb, f"Push {nb} on the stack"))
        peak = max(peak, len(stack))
        if pushed == 0 and record_events:
            events.append(make_event(
                "dead_end", cell, f"Dead end at {cell}: pop the stack to jump to another branch"))

    if record_events:
        events.append(make_event("no_path", start, "Stack is empty: there is no path to the goal"))
    return make_result("DFS", False, [], visit_order, events, 0, peak)
