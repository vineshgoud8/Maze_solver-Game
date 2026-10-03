"""
app.py - Maze Solver Game (Streamlit user interface)

Run with:   streamlit run app.py
"""

import math
import time

import matplotlib.pyplot as plt
import streamlit as st

from maze import generate_maze, parse_maze, grid_to_text, WALL, OPEN, START, GOAL
from metrics import ALGORITHMS, run_algorithm, compare_all, results_to_dataframe, summary_notes, format_time
from visualization import build_state, draw_maze, comparison_chart, legend_html

MAX_FRAMES = 150      # the replay is split into at most this many pictures

st.set_page_config(page_title="Maze Solver Game", page_icon="🧩", layout="wide")

st.markdown("""
<style>
.hero {background: linear-gradient(90deg,#1e3a8a,#7c3aed); padding: 1.1rem 1.5rem;
       border-radius: 14px; color: white; margin-bottom: 0.8rem;}
.hero h1 {margin: 0; font-size: 2.1rem; color: white;}
.hero p {margin: 0.2rem 0 0 0; font-size: 1.1rem; opacity: 0.9;}
.stepbox {background:#f1f5f9; border-left: 5px solid #f97316; padding: 0.6rem 0.9rem;
          border-radius: 6px; color:#0f172a; font-size: 1.0rem;}
</style>
<div class="hero"><h1>🧩 Maze Solver Game</h1><p>Visualize. Explore. Compare.</p></div>
""", unsafe_allow_html=True)

ALGO_INFO = {
    "BFS": ("Breadth-First Search", "Queue (first in, first out)",
            "Explores the maze in rings (level by level). In an unweighted maze, where every move costs 1, "
            "BFS **guarantees the shortest path**. It may visit many cells to do so."),
    "DFS": ("Depth-First Search", "Stack (last in, first out)",
            "Goes as deep as possible down one corridor and only jumps to another branch when stuck. "
            "It finds **a** path, but **not necessarily the shortest**."),
    "Backtracking": ("Recursive Backtracking", "Recursion (call stack) + current-path list",
                     "Choose a cell, explore from it, and if it is a dead end **undo** the choice and try another. "
                     "On a grid maze it searches like DFS, but it keeps a visible current path and counts every undo."),
}

# ----------------------------------------------------------------------------
# Session state (Streamlit forgets variables on every click, so we store them)
# ----------------------------------------------------------------------------
def init_state():
    if "grid" not in st.session_state:
        grid, start, goal = generate_maze(21, "Medium")
        st.session_state.update(grid=grid, start=start, goal=goal, results={}, frame=0,
                                max_frame=0, stride=1, rid=0, maze_id=0, play_request=False)

init_state()
S = st.session_state


def bump():
    """Results changed: start the replay again from the beginning."""
    S.rid += 1
    S.frame = 0


def set_maze(grid, start, goal):
    S.grid, S.start, S.goal = grid, start, goal
    S.results = {}
    S.maze_id += 1
    bump()


def go_to(frame):
    S.frame = max(0, min(S.max_frame, frame))


def cb_slider(key):
    S.frame = S[key]


def cb_play():
    S.play_request = True


# ----------------------------------------------------------------------------
# Sidebar: settings
# ----------------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Maze Settings")
    size = st.slider("Maze size", 11, 41, 21, step=2, help="Odd numbers only. Bigger = slower animation.")
    difficulty = st.select_slider("Difficulty", ["Easy", "Medium", "Hard"], value="Medium",
                                  help="Easy: many shortcuts. Hard: exactly one route and many dead ends.")
    seed_in = st.number_input("Maze seed (0 = random)", min_value=0, value=0, step=1,
                              help="Use the same seed to get the same maze again.")
    algo = st.radio("Algorithm", list(ALGORITHMS.keys()))
    speed = st.slider("Animation speed", 1, 10, 6)
    trials = st.slider("Timing trials (average)", 1, 50, 20,
                       help="Each algorithm is timed this many times and the average is shown.")
    st.divider()
    st.markdown("**Legend**")
    st.markdown(legend_html(), unsafe_allow_html=True)
    st.caption("BFS: shade of yellow shows the level (distance from the start).")

# ----------------------------------------------------------------------------
# Main buttons
# ----------------------------------------------------------------------------
b1, b2, b3, b4 = st.columns(4)
if b1.button("🎲 Generate Maze"):
    try:
        g, s, t = generate_maze(size, difficulty, int(seed_in) if seed_in else None)
        set_maze(g, s, t)
    except (ValueError, RuntimeError) as err:
        st.error(str(err))
if b2.button("▶️ Solve"):
    S.results[algo] = run_algorithm(algo, S.grid, S.start, S.goal, trials)
    bump()
if b3.button("📊 Compare All"):
    S.results = compare_all(S.grid, S.start, S.goal, trials)
    bump()
if b4.button("↩️ Reset"):
    S.results = {}
    bump()

grid, start, goal = S.grid, S.start, S.goal
rows, cols = len(grid), len(grid[0])
open_cells = sum(ch != WALL for row in grid for ch in row)
st.caption(f"Maze: {rows} x {cols} grid, {open_cells} open cells. Start S = {start}, Goal G = {goal}. "
           "The same maze is used for every algorithm.")

with st.expander("✏️ Create or edit a maze manually"):
    st.write("Use `S` (start), `G` (goal), `.` (open) and `#` (wall). Exactly one S and one G; all rows the same length.")
    text = st.text_area("Maze text", value=grid_to_text(grid), height=260, key=f"maze_text_{S.maze_id}")
    if st.button("Use this maze"):
        try:
            g, s, t = parse_maze(text)
            set_maze(g, s, t)
            st.rerun()
        except ValueError as err:
            st.error(f"Invalid maze: {err}")
    st.write("Or flip a single cell between wall and open:")
    e1, e2, e3 = st.columns(3)
    er = e1.number_input("Row", 0, rows - 1, 0)
    ec = e2.number_input("Column", 0, cols - 1, 0)
    if e3.button("Toggle cell"):
        cell = (int(er), int(ec))
        if cell in (start, goal):
            st.error("You cannot change the start or the goal cell.")
        else:
            g = [row[:] for row in grid]
            g[cell[0]][cell[1]] = OPEN if g[cell[0]][cell[1]] == WALL else WALL
            set_maze(g, start, goal)
            st.rerun()

# ----------------------------------------------------------------------------
# Visualizer + results
# ----------------------------------------------------------------------------
left, right = st.columns([3, 2])
result = S.results.get(algo)

with left:
    st.subheader(f"🎬 {algo} visualizer")
    fig_slot = st.empty()
    msg_slot = st.empty()

    if result is None:
        fig = draw_maze(grid, start, goal, title="Your maze")
        fig_slot.pyplot(fig)
        plt.close(fig)
        msg_slot.info(f"Press **Solve** to watch {algo}, or **Compare All** to run all three algorithms.")
    else:
        events = result["events"]
        n = len(events)
        stride = max(1, math.ceil(n / MAX_FRAMES))
        S.stride, S.max_frame = stride, math.ceil(n / stride)
        S.frame = max(0, min(S.frame, S.max_frame))

        def render(frame):
            k = min(frame * stride, n)
            state = build_state(events, k)
            fig = draw_maze(grid, start, goal, state, title=f"{algo}: step {k} of {n}")
            fig_slot.pyplot(fig)
            plt.close(fig)
            text_ = events[k - 1]["msg"] if k > 0 else "Press ▶ Play or Next to begin."
            msg_slot.markdown(f'<div class="stepbox"><b>What is happening:</b> {text_}</div>',
                              unsafe_allow_html=True)

        # keep the slider in sync with the real frame BEFORE the slider is created
        slider_key = f"frame_slider_{S.rid}"
        S[slider_key] = S.frame

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.button("⏮ Start", on_click=go_to, args=(0,))
        c2.button("◀ Prev", on_click=go_to, args=(S.frame - 1,))
        c3.button("▶ Play", on_click=cb_play)
        c4.button("Next ▶", on_click=go_to, args=(S.frame + 1,))
        c5.button("⏭ End", on_click=go_to, args=(S.max_frame,))
        if S.max_frame > 0:
            st.slider("Step", 0, S.max_frame, key=slider_key, on_change=cb_slider, args=(slider_key,))
        st.caption("Tip: clicking any button while playing pauses the animation.")

        play_now = S.play_request
        S.play_request = False               # consume the request: later clicks will not replay
        if play_now:
            first = 0 if S.frame >= S.max_frame else S.frame
            delay = 0.6 / speed
            for f in range(first, S.max_frame + 1):
                S.frame = f                  # remember progress so that Pause keeps this picture
                render(f)
                time.sleep(delay)
            st.rerun()
        else:
            render(S.frame)

with right:
    st.subheader("📈 Results")
    if result is None:
        st.write("Results will appear here after you press **Solve**.")
    else:
        if result["found"]:
            st.success(f"{algo}: solution found")
        else:
            st.warning(f"{algo}: no path exists in this maze")
        m1, m2 = st.columns(2)
        m1.metric("Path Length (steps)", result["path_length"] if result["found"] else "-")
        m2.metric("Visited Cells", result["visited_count"])
        m3, m4 = st.columns(2)
        m3.metric(f"Avg Time ({result['trials']} runs)", format_time(result["time_ms"]))
        m4.metric("Backtracking Count", result["backtrack_count"] if algo == "Backtracking" else "n/a")
        st.caption(f"Time range over {result['trials']} runs: {format_time(result['time_min_ms'])} "
                   f"to {format_time(result['time_max_ms'])}. On small mazes times are tiny and noisy.")
    name_full, structure, blurb = ALGO_INFO[algo]
    st.markdown(f"**{name_full}** - uses a {structure}")
    st.write(blurb)

# ----------------------------------------------------------------------------
# Comparison, explanations
# ----------------------------------------------------------------------------
tab1, tab2, tab3 = st.tabs(["📊 Comparison", "📚 How each algorithm works", "ℹ️ About fairness"])

with tab1:
    if len(S.results) < 2:
        st.info("Press **Compare All** to run BFS, DFS and Backtracking on this same maze.")
    else:
        st.dataframe(results_to_dataframe(S.results), hide_index=True)
        cfig = comparison_chart(S.results)
        st.pyplot(cfig)
        plt.close(cfig)
        for note in summary_notes(S.results):
            st.write("- " + note)
        st.markdown("**Final picture of each search** (same maze):")
        cols_ = st.columns(len(S.results))
        for col, (name, r) in zip(cols_, S.results.items()):
            state = build_state(r["events"], len(r["events"]))
            f = draw_maze(grid, start, goal, state, title=name, figsize=(4, 4))
            col.pyplot(f)
            plt.close(f)
        st.caption("No algorithm is best for everything: each one trades path quality, "
                   "cells explored and memory in a different way.")

with tab2:
    for name, (full, structure, blurb) in ALGO_INFO.items():
        st.markdown(f"#### {full}")
        st.write(f"**Data structure:** {structure}")
        st.write(blurb)
    st.markdown("""
**Choose → Explore → Dead End → Undo → Try another choice** is the heart of backtracking.
Watch the *light-blue* cells (current path) grow, and the *purple* cells (undone) appear when a branch fails.

| | BFS | DFS | Backtracking |
|---|---|---|---|
| Shortest path guaranteed? | Yes (unweighted) | No | No |
| Main structure | Queue | Stack | Recursion |
| Time complexity | O(R x C) | O(R x C) | O(R x C) here (cells are marked as tried) |
| Memory | Can be large (whole ring) | Usually smaller | Depth of the current path |
""")

with tab3:
    st.markdown("""
- All algorithms run on **exactly the same maze, start and goal**.
- Every algorithm builds **fresh** data structures on each run and never edits the maze.
- Time is measured with Python's `time.perf_counter()` and **averaged over several trials**; animation events are *not* recorded while timing.
- Neighbour order is identical for all algorithms: Up, Right, Down, Left.
- DFS and Backtracking use the same neighbour order and mark visited cells, so on a grid maze they often visit the same cells; they differ in *how* they work and what they report.
- Results depend on the maze. This app does **not** claim any algorithm is always best.
""")
