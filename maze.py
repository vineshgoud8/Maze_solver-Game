"""
maze.py - Maze representation, generation, parsing and helper functions.

The maze is a 2D grid (a list of rows, each row is a list of single characters):

    S = Start      G = Goal      . = Open cell      # = Wall

A "cell" is always a tuple (row, col).  Row 0 is the top row.
"""

import random

WALL, OPEN, START, GOAL = "#", ".", "S", "G"

# The four moves we allow: Up, Right, Down, Left.
# Every algorithm uses THIS SAME ORDER so the comparison is fair.
DIRECTIONS = [(-1, 0), (0, 1), (1, 0), (0, -1)]

# Difficulty = how many extra "shortcuts" (loops) we knock into a perfect maze.
#   Easy   -> many shortcuts, many routes, lots of open space
#   Medium -> a few shortcuts
#   Hard   -> no shortcuts: exactly ONE route and many dead ends
LOOP_FRACTION = {"Easy": 0.25, "Medium": 0.08, "Hard": 0.0}

MIN_SIZE, MAX_SIZE = 7, 41


# --------------------------------------------------------------------------
# Small helpers used by every algorithm
# --------------------------------------------------------------------------
def make_event(kind, cell, msg="", **extra):
    """Create one search event.  The UI replays these to animate the search.

    kind is one of: visit, explore, choose, dead_end, backtrack, goal, path, no_path
    """
    event = {"type": kind, "cell": cell, "msg": msg}
    event.update(extra)
    return event


def neighbors(grid, cell):
    """Return the walkable neighbours of a cell, in the fixed DIRECTIONS order."""
    rows, cols = len(grid), len(grid[0])
    r, c = cell
    result = []
    for dr, dc in DIRECTIONS:
        nr, nc = r + dr, c + dc
        if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != WALL:
            result.append((nr, nc))
    return result


def reconstruct_path(parent, goal):
    """Walk backwards from the goal using the parent links, then reverse."""
    path = []
    cell = goal
    while cell is not None:
        path.append(cell)
        cell = parent[cell]
    path.reverse()
    return path


def make_result(name, found, path, visit_order, events, backtracks=0, peak=0):
    """Build the standard result dictionary that every algorithm returns."""
    return {
        "algorithm": name,
        "found": found,
        "path": path if found else [],
        # Path length is counted in STEPS (moves) = number of cells on the path - 1
        "path_length": (len(path) - 1) if found else None,
        "visit_order": visit_order,
        "visited_count": len(visit_order),
        "backtrack_count": backtracks,
        "peak_size": peak,          # biggest queue / stack / recursion depth
        "events": events,
    }


def find_cell(grid, symbol):
    """Return the (row, col) of the first cell equal to symbol, or None."""
    for r, row in enumerate(grid):
        for c, ch in enumerate(row):
            if ch == symbol:
                return (r, c)
    return None


def is_valid_path(grid, path, start, goal):
    """Check a path: starts at S, ends at G, every step is one move, no walls."""
    if not path or path[0] != start or path[-1] != goal:
        return False
    for a, b in zip(path, path[1:]):
        if abs(a[0] - b[0]) + abs(a[1] - b[1]) != 1:
            return False
    return all(grid[r][c] != WALL for r, c in path)


# --------------------------------------------------------------------------
# Text <-> grid conversion (used by the manual maze editor)
# --------------------------------------------------------------------------
def grid_to_text(grid):
    return "\n".join("".join(row) for row in grid)


def parse_maze(text):
    """Turn text into (grid, start, goal).  Raises ValueError with a clear message."""
    lines = [ln.strip() for ln in text.strip().splitlines() if ln.strip()]
    if len(lines) < 3:
        raise ValueError("The maze needs at least 3 rows.")
    width = len(lines[0])
    if width < 3:
        raise ValueError("The maze needs at least 3 columns.")
    if any(len(ln) != width for ln in lines):
        raise ValueError("All rows must have the same length.")
    allowed = {WALL, OPEN, START, GOAL}
    bad = {ch for ln in lines for ch in ln} - allowed
    if bad:
        raise ValueError("Only the characters S G . # are allowed. Found: " + " ".join(sorted(bad)))
    grid = [list(ln) for ln in lines]
    starts = sum(row.count(START) for row in grid)
    goals = sum(row.count(GOAL) for row in grid)
    if starts != 1:
        raise ValueError(f"The maze must contain exactly one S (found {starts}).")
    if goals != 1:
        raise ValueError(f"The maze must contain exactly one G (found {goals}).")
    return grid, find_cell(grid, START), find_cell(grid, GOAL)


# --------------------------------------------------------------------------
# Maze generation
# --------------------------------------------------------------------------
def generate_maze(size=21, difficulty="Medium", seed=None, max_attempts=50):
    """Generate a random SOLVABLE maze.

    Steps
      1. Start with a grid full of walls.
      2. Carve passages with a randomized depth-first walk (this makes a "perfect"
         maze: every open cell is connected and there is exactly one route
         between any two cells).
      3. Knock out a few extra walls to create loops (more loops = easier).
      4. Put S in the top-left and G in the bottom-right.
      5. Verify with BFS that G can be reached; if not, generate again.
    """
    from bfs import bfs  # imported here to avoid a circular import at load time

    if difficulty not in LOOP_FRACTION:
        raise ValueError(f"Unknown difficulty '{difficulty}'. Choose Easy, Medium or Hard.")
    try:
        size = int(size)
    except (TypeError, ValueError):
        raise ValueError("Maze size must be a whole number.")
    size = max(MIN_SIZE, min(MAX_SIZE, size))
    if size % 2 == 0:          # the carving method needs an odd size
        size += 1

    rng = random.Random(seed)
    for _ in range(max_attempts):
        grid = _carve_perfect_maze(size, rng)
        _add_loops(grid, LOOP_FRACTION[difficulty], rng)
        start, goal = (1, 1), (size - 2, size - 2)
        grid[start[0]][start[1]] = START
        grid[goal[0]][goal[1]] = GOAL
        if bfs(grid, start, goal, record_events=False)["found"]:
            return grid, start, goal
    raise RuntimeError("Could not generate a solvable maze. Please try again.")


def _carve_perfect_maze(size, rng):
    grid = [[WALL] * size for _ in range(size)]
    grid[1][1] = OPEN
    stack = [(1, 1)]
    while stack:
        r, c = stack[-1]
        # Look two cells away (the cell in between is the wall we may remove)
        options = []
        for dr, dc in DIRECTIONS:
            nr, nc = r + 2 * dr, c + 2 * dc
            if 1 <= nr < size - 1 and 1 <= nc < size - 1 and grid[nr][nc] == WALL:
                options.append((dr, dc))
        if options:
            dr, dc = rng.choice(options)
            grid[r + dr][c + dc] = OPEN
            grid[r + 2 * dr][c + 2 * dc] = OPEN
            stack.append((r + 2 * dr, c + 2 * dc))
        else:
            stack.pop()   # dead end of the carving walk -> go back
    return grid


def _add_loops(grid, fraction, rng):
    """Remove a fraction of the walls that separate two open corridors."""
    size = len(grid)
    candidates = []
    for r in range(1, size - 1):
        for c in range(1, size - 1):
            if grid[r][c] != WALL:
                continue
            horizontal = grid[r][c - 1] != WALL and grid[r][c + 1] != WALL
            vertical = grid[r - 1][c] != WALL and grid[r + 1][c] != WALL
            if horizontal != vertical:      # wall sits between exactly two corridors
                candidates.append((r, c))
    rng.shuffle(candidates)
    for r, c in candidates[: int(len(candidates) * fraction)]:
        grid[r][c] = OPEN


def is_solvable(grid, start, goal):
    """True if BFS can reach the goal from the start."""
    from bfs import bfs
    return bfs(grid, start, goal, record_events=False)["found"]
