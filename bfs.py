"""
bfs.py - Breadth-First Search (BFS)

IDEA: explore the maze in "rings" (levels).  First every cell 1 step from the start,
then every cell 2 steps away, then 3 steps ... A QUEUE (first in, first out) does
this naturally.  Because we always finish a level before starting the next one,
the first time we reach the goal we have used the FEWEST possible steps.
=> BFS guarantees the shortest path in an unweighted maze (every move costs 1).
"""

from collections import deque
from maze import make_event, neighbors, reconstruct_path, make_result


def bfs(grid, start, goal, record_events=True):
    queue = deque([start])          # cells waiting to be explored (FIFO)
    discovered = {start}            # cells already added to the queue
    parent = {start: None}          # parent[cell] = the cell we came from
    level = {start: 0}              # level[cell] = number of steps from the start
    visit_order = []                # order in which cells are explored
    events = []
    peak = 1

    while queue:
        cell = queue.popleft()      # take from the FRONT of the queue
        visit_order.append(cell)
        if record_events:
            events.append(make_event(
                "visit", cell, f"Level {level[cell]}: take {cell} from the front of the queue",
                level=level[cell]))

        if cell == goal:            # reached the goal -> rebuild the path
            path = reconstruct_path(parent, goal)
            if record_events:
                events.append(make_event("goal", cell, "Goal reached!"))
                events.append(make_event(
                    "path", cell, f"Shortest path found: {len(path) - 1} steps", path=path))
            return make_result("BFS", True, path, visit_order, events, 0, peak)

        for nb in neighbors(grid, cell):
            if nb not in discovered:            # never add the same cell twice
                discovered.add(nb)
                parent[nb] = cell
                level[nb] = level[cell] + 1
                queue.append(nb)                # add to the BACK of the queue
                peak = max(peak, len(queue))
                if record_events:
                    events.append(make_event(
                        "explore", nb, f"Add {nb} to the back of the queue"))

    # Queue is empty and the goal was never reached
    if record_events:
        events.append(make_event("no_path", start, "Queue is empty: there is no path to the goal"))
    return make_result("BFS", False, [], visit_order, events, 0, peak)
