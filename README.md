# 🧩 Maze Solver Game — Comparing BFS, DFS and Backtracking

> **Visualize. Explore. Compare.**
> *Don't just learn how algorithms work — watch them work.*

## Project description
An interactive Streamlit web app that generates (or accepts) a maze and solves the **same** maze with
**BFS**, **DFS** and **Recursive Backtracking**. Every algorithm records its search events (visit, explore,
choose, dead end, backtrack, goal, path), and the app **replays those events step by step**, so you can see *how*
the answer is found, not only the final path. Results are compared by path length, visited cells,
execution time and backtracking count.

## Problem statement
Generate or accept a maze and let users compare BFS, DFS and Backtracking solutions by path length, number of
visited cells and execution time. The system should make the algorithm's important decisions visible rather than only
displaying the final answer.

## Objectives
1. Implement BFS, DFS and Backtracking correctly.
2. Visualize each search step by step.
3. Compare the algorithms fairly on the same maze with measurable results.
4. Keep the project simple, beginner-friendly and runnable locally.

## Features
- Random **solvable** maze generator (verified with BFS) with **Easy / Medium / Hard** difficulty
- Manual maze creation/editing (text editor + single-cell toggle) with input validation
- Algorithm selection, animation speed, Play / Step / Prev / Start / End and a step slider
- Colour-coded visualization with a plain-English "what is happening" message for every step
- Metrics: path length, visited cells, average execution time, backtracking count, solution found
- **Compare All** table, bar charts and final-state pictures for all three algorithms on the same maze
- Handles unsolvable mazes, invalid input, and start/goal edge cases

## Algorithms
| | BFS | DFS | Backtracking |
|---|---|---|---|
| Idea | Explore level by level | Go deep, then try another branch | Choose → Explore → Dead end → Undo |
| Structure | Queue | Stack | Recursion + current-path list |
| Shortest path? | **Yes** (unweighted maze) | No | No |
| Time | O(R×C) | O(R×C) | O(R×C) (cells are marked as tried) |

> Honest note: on a grid maze with visited-marking, DFS and Backtracking explore cells in the same order. They
> differ in *mechanism* and in what is visible: Backtracking keeps a current path and counts every undo.
> No algorithm is "best" for every maze.

## Technology stack
Python 3.9+ · Streamlit · Matplotlib · NumPy · pandas

## Project structure
```
maze_solver_game/
├── app.py              # Streamlit user interface
├── maze.py             # grid, generator, parser, helpers
├── bfs.py              # Breadth-First Search
├── dfs.py              # Depth-First Search
├── backtracking.py     # Recursive Backtracking
├── metrics.py          # fair runner, timing, comparison table
├── visualization.py    # event replay + drawing
├── test_algorithms.py  # automated tests
├── run_benchmarks.py   # prints real numbers for your report
├── requirements.txt
└── README.md
```

## Installation
```bash
cd maze_solver_game
python -m venv venv                 # optional
venv\Scripts\activate               # Windows   (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
```

## How to run
```bash
streamlit run app.py
```
Run the tests with `python test_algorithms.py`. Print benchmark numbers with `python run_benchmarks.py`.

## How to use
1. Choose size, difficulty and algorithm in the sidebar, then press **Generate Maze**.
2. Press **Solve**, then **Play** (or use **Next ▶** / the slider to go step by step).
3. Read the yellow message box: it explains each decision.
4. Press **Reset**, pick another algorithm and **Solve** again on the same maze.
5. Press **Compare All** to see the table, charts and final pictures side by side.
6. Open *Create or edit a maze manually* to type your own maze.

**Colours:** green = start · red = goal · dark = wall · yellow = visited · teal = waiting (queue/stack) ·
orange = current cell · light blue = current path (backtracking) · purple = backtracked (undone) · deep blue = final path

## Algorithm comparison (fill in from your own run)
| Maze | Algorithm | Path length | Visited | Backtracks | Avg time |
|---|---|---|---|---|---|
| [your maze] | BFS | [INSERT] | [INSERT] | n/a | [INSERT] |
| [your maze] | DFS | [INSERT] | [INSERT] | n/a | [INSERT] |
| [your maze] | Backtracking | [INSERT] | [INSERT] | [INSERT] | [INSERT] |

## Screenshots
*(Add your screenshots here)*
- `screenshots/home.png` · `screenshots/bfs.png` · `screenshots/dfs.png` · `screenshots/backtracking.png` · `screenshots/compare.png`

## Future improvements
A* and Dijkstra, weighted cells, click-to-draw maze editor, other generators (Prim, Kruskal), diagonal moves,
benchmark mode over many mazes, export results to CSV, step-by-step pseudocode highlighting.
