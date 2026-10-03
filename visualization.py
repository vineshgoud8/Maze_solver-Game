"""
visualization.py - Turn search events into pictures (Matplotlib).

replay idea:  events[0..k]  --build_state-->  a "snapshot"  --draw_maze-->  a picture
Showing a bigger k each time gives the step-by-step animation.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import to_rgb

from maze import WALL

COLORS = {
    "Start": "#22C55E",
    "Goal": "#EF4444",
    "Wall": "#1F2937",
    "Open cell": "#F8FAFC",
    "Waiting (queue / stack)": "#99F6E4",
    "Visited": "#FACC15",
    "Current cell": "#F97316",
    "Current path (backtracking)": "#60A5FA",
    "Backtracked (undone)": "#A855F7",
    "Final path": "#1D4ED8",
}
ALGO_COLORS = {"BFS": "#2563EB", "DFS": "#F59E0B", "Backtracking": "#9333EA"}


def legend_html():
    """A small HTML legend (used by the Streamlit app)."""
    items = "".join(
        f'<span style="display:inline-block;margin:2px 10px 2px 0;font-size:0.85rem;">'
        f'<span style="display:inline-block;width:14px;height:14px;background:{col};'
        f'border:1px solid #94a3b8;border-radius:3px;vertical-align:middle;margin-right:5px;"></span>{name}</span>'
        for name, col in COLORS.items())
    return f"<div>{items}</div>"


def build_state(events, k):
    """Apply the first k events and return what the maze should look like."""
    s = {"visited": set(), "frontier": set(), "current": None, "path": [],
         "backtracked": set(), "final_path": [], "found": False, "level": {}}
    for e in events[:k]:
        kind, cell = e["type"], e["cell"]
        if kind == "explore":
            if cell not in s["visited"]:
                s["frontier"].add(cell)
        elif kind == "visit":
            s["visited"].add(cell)
            s["frontier"].discard(cell)
            s["current"] = cell
            if "level" in e:
                s["level"][cell] = e["level"]
        elif kind == "choose":
            s["visited"].add(cell)
            s["frontier"].discard(cell)
            s["path"].append(cell)
            s["current"] = cell
        elif kind == "dead_end":
            s["current"] = cell
        elif kind == "backtrack":
            if s["path"]:
                s["path"].pop()
            s["backtracked"].add(cell)
            s["current"] = s["path"][-1] if s["path"] else None
        elif kind == "goal":
            s["current"] = cell
            s["found"] = True
        elif kind == "path":
            s["final_path"] = list(e["path"])
    return s


def _level_color(level):
    """BFS: pale yellow -> amber in repeating bands, so each 'ring' (level) is visible."""
    a, b = np.array(to_rgb("#FEF08A")), np.array(to_rgb("#F59E0B"))
    t = (level % 8) / 7.0
    return tuple(a + (b - a) * t)


def draw_maze(grid, start, goal, state=None, title="", figsize=(6, 6)):
    """Draw the maze (and optionally a replay snapshot). Returns a Matplotlib figure."""
    rows, cols = len(grid), len(grid[0])
    img = np.zeros((rows, cols, 3))
    open_c, wall_c = to_rgb(COLORS["Open cell"]), to_rgb(COLORS["Wall"])
    for r in range(rows):
        for c in range(cols):
            img[r, c] = wall_c if grid[r][c] == WALL else open_c

    if state:
        for cell in state["frontier"]:
            img[cell] = to_rgb(COLORS["Waiting (queue / stack)"])
        for cell in state["visited"]:
            if cell in state["level"]:
                img[cell] = _level_color(state["level"][cell])
            else:
                img[cell] = to_rgb(COLORS["Visited"])
        for cell in state["backtracked"]:
            img[cell] = to_rgb(COLORS["Backtracked (undone)"])
        for cell in state["path"]:
            img[cell] = to_rgb(COLORS["Current path (backtracking)"])
        for cell in state["final_path"]:
            img[cell] = to_rgb(COLORS["Final path"])
        if state["current"] is not None and not state["final_path"]:
            img[state["current"]] = to_rgb(COLORS["Current cell"])

    img[start] = to_rgb(COLORS["Start"])
    img[goal] = to_rgb(COLORS["Goal"])

    fig, ax = plt.subplots(figsize=figsize)
    ax.imshow(img, interpolation="nearest")
    ax.set_xticks(np.arange(-0.5, cols, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, rows, 1), minor=True)
    ax.grid(which="minor", color="#CBD5E1", linewidth=0.4)
    ax.tick_params(which="both", bottom=False, left=False, labelbottom=False, labelleft=False)
    for spine in ax.spines.values():
        spine.set_visible(False)
    fs = max(6, min(14, 130 // max(rows, cols)))
    ax.text(start[1], start[0], "S", ha="center", va="center", color="white", fontsize=fs, fontweight="bold")
    ax.text(goal[1], goal[0], "G", ha="center", va="center", color="white", fontsize=fs, fontweight="bold")
    if title:
        ax.set_title(title, fontsize=11, fontweight="bold")
    fig.tight_layout()
    return fig


def comparison_chart(results):
    """Three side-by-side bar charts: path length, visited cells, average time."""
    names = list(results.keys())
    colors = [ALGO_COLORS.get(n, "#64748B") for n in names]
    paths = [r["path_length"] if r["found"] else 0 for r in results.values()]
    visited = [r["visited_count"] for r in results.values()]
    times = [r["time_ms"] for r in results.values()]

    fig, axes = plt.subplots(1, 3, figsize=(11, 3.4))
    for ax, values, title, fmt in (
        (axes[0], paths, "Path length (steps)", "{:d}"),
        (axes[1], visited, "Visited cells", "{:d}"),
        (axes[2], times, "Average time (ms)", "{:.4f}"),
    ):
        bars = ax.bar(names, values, color=colors)
        ax.set_title(title, fontsize=10, fontweight="bold")
        ax.spines[["top", "right"]].set_visible(False)
        ax.tick_params(axis="x", labelsize=8)
        for bar, v in zip(bars, values):
            ax.annotate(fmt.format(v), (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                        ha="center", va="bottom", fontsize=8)
        ax.margins(y=0.15)
    fig.tight_layout()
    return fig
