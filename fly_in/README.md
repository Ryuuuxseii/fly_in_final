*This project has been created as part of the 42 curriculum by fjose-hi.*

# Fly-in — Drone Routing Simulation

## Description

Fly-in is a drone routing simulation system written in Python 3.10+. The goal is to route a fleet of drones from a start zone to a target end zone through a network of connected zones, minimizing the total number of simulation turns while respecting strict movement and capacity constraints.

The system parses a custom map file format, builds a graph of zones and connections, computes optimal paths using a weighted Dijkstra algorithm with iterative penalty-based diversification, and simulates the turn-by-turn movement of all drones simultaneously. It produces a step-by-step log of drone movements and provides colored terminal output, a static graph visualization (matplotlib), and an interactive step-by-step animation (pygame).

## Instructions

### Requirements

- Python 3.10 or later
- pip or any compatible package manager

### Installation

```bash
make install
```

Creates a virtual environment in `.venv/` and installs all dependencies from `requirements.txt`.

### Running the simulation

```bash
# Static mode: run simulation then display graph (matplotlib)
make run

# Static mode with a specific map
make run MAP=maps/easy/01_linear_path.txt

# Animation mode: interactive step-by-step visualization (pygame)
make animate

# Animation mode with a specific map
make animate MAP=maps/hard/01_maze_nightmare.txt
```

### Other commands

```bash
make debug          # Run in debug mode with pdb
make lint           # Run flake8 + mypy with mandatory flags
make lint-strict    # Run flake8 + mypy with --strict
make clean          # Remove __pycache__, .mypy_cache, .pytest_cache, *.pyc, *.pyo
make fclean         # clean + remove the virtual environment
make help           # Show all available targets
```

### Map file format

```
nb_drones: 5
start_hub: hub 0 0 [color=green]
end_hub: goal 10 10 [color=yellow]
hub: roof1 3 4 [zone=restricted color=red]
hub: corridorA 4 3 [zone=priority color=green max_drones=2]
hub: obstacleX 5 5 [zone=blocked color=gray]
connection: hub-roof1
connection: hub-corridorA
connection: corridorA-goal [max_link_capacity=2]
```

Zone types:
 
- `normal` — standard zone, 1 turn to enter (default)
- `restricted` — sensitive zone, 2 turns to enter (drone occupies the connection during the first turn and must arrive on the second)
- `priority` — preferred zone, 1 turn to enter, same 1 turn cost as normal zones but preferred by the pathfinder when two routes tie
- `blocked` — inaccessible, drones cannot enter or pass through

### Example input and expected output

**Map file** (`maps/easy/01_linear_path.txt`):
```
nb_drones: 2
start_hub: start 0 0 [color=green]
end_hub: goal 3 0 [color=yellow]
hub: mid1 1 0
hub: mid2 2 0
connection: start-mid1
connection: mid1-mid2
connection: mid2-goal
```

**Expected output**:
```
D1-mid1
D1-mid2 D2-mid1
D1-goal D2-mid2
D2-goal

Simulation complete!
  Total turns  : 4
  Drones delivered: 2
```

Each line is one simulation turn. `D<ID>-<zone>` means drone D\<ID\> moved to that zone. Drones that do not move in a given turn are omitted. When a drone moves toward a `restricted` zone, the format is `D<ID>-<zoneA>-<zoneB>` for the first turn (in transit) and `D<ID>-<zoneB>` for the arrival turn.

## Algorithm Explanation

### Pathfinding — Dijkstra with iterative penalty diversification

Implemented from scratch in `src/pathfinding.py`. No graph libraries are used.

**Core algorithm:** Dijkstra's algorithm finds the shortest weighted path from the start zone to the end zone. Each zone has a movement weight based on its type: `normal` and `priority` zones both cost 1.0, `restricted` zones 2.0, and `blocked` zones are excluded entirely from the search. When two routes reach a neighbor with equal cost, `priority` zones are always preferred over `normal` zones via an explicit tiebreaker in node selection and path recording.

**Path diversification:** To distribute drones across multiple routes and avoid bottlenecks, the algorithm is run iteratively up to `max_paths` times. After each path is found, a penalty of 1.5 is added to every intermediate zone on that path. This causes the next Dijkstra run to explore alternative routes. Up to 4 diverse paths are computed (2 for maps with 25+ drones to reduce initialization time), and drones are assigned to these paths in round-robin order.

**Complexity:** Each Dijkstra run is O(V²) using a list-based min selection (V = number of zones). The penalty loop runs up to `max_paths` times, so total pathfinding cost is O(max_paths × V²). For the maps in this project this is negligible.

### Simulation — Turn-by-turn synchronous scheduling

Implemented in `src/simulation.py`. Each call to `_run_turn` processes all drones simultaneously in a single pass:

1. **Transit arrivals first:** Drones that entered a `restricted` zone on the previous turn (marked `in_transit=True`) arrive at their destination. Arrival respects `max_drones` capacity of the destination zone.
2. **Candidate selection:** All non-delivered, non-transiting drones with a valid next step are collected as candidates.
3. **Move validation:** For each candidate, `_can_move` checks:
   - The connection between the current and next zone exists.
   - The connection's `max_link_capacity` is not already saturated for this turn.
   - The destination zone's `max_drones` will not be exceeded (accounting for drones already leaving that zone and drones already entering it this turn, plus any future in-transit arrivals for restricted zones).
   - Start and end zones are always accepted regardless of occupancy.
4. **Movement execution:** Drones moving to a `restricted` zone are placed `in_transit` and logged as `D<ID>-<origin>-<dest>`. All others move immediately.

**Deadlock detection:** If no drone moves for 20 consecutive turns, a `SimulationDeadlockError` is raised and caught in `main.py` with a clean error message and exit code 1.

**Path caching:** Paths are computed once at initialization and stored per drone. There is no per-turn recalculation. If a drone is blocked it simply waits in place; its stored path remains unchanged.

### Performance results

| Map | Drones | Result | Target |
|---|---|---|---|
| Easy 1 — Linear path | 2 | 4 turns | ≤ 6 |
| Easy 2 — Simple fork | 4 | 4 turns | ≤ 8 |
| Easy 3 — Basic capacity | 4 | 4 turns | ≤ 6 |
| Medium 1 — Dead end trap | 5 | 8 turns | ≤ 12 |
| Medium 2 — Circular loop | 6 | 15 turns | ≤ 15 |
| Medium 3 — Priority puzzle | 5 | 7 turns | ≤ 12 |
| Hard 1 — Maze nightmare | 8 | 13 turns | ≤ 30 |
| Hard 2 — Capacity hell | 12 | 16 turns | ≤ 35 |
| Hard 3 — Ultimate challenge | 15 | 27 turns | ≤ 45 |
| Challenger — The Impossible Dream | 25 | **44 turns** | ≤ 45 (record) |

All targets met or beaten. The challenger map beats the reference record of 45 turns.

## Visual Representation

### Terminal output — colorama (`make run` / `make animate`)

Every simulation turn is printed to the terminal with colored output. Drone identifiers (`D1`, `D2`, …) are highlighted in yellow. Zone names are colored using the color defined in the map file (e.g. `color=red` renders in red). This makes it easy to follow drone movements and spot zone types at a glance without opening the graphical window.

Supported terminal colors: `green`, `blue`, `red`, `yellow`, `gray`, `orange`, `purple`, `cyan`, `white`, `black`, `brown`, `lime`, `magenta`, `gold`, `pink`, `teal`, `maroon`, `darkred`, `violet`, `crimson`.

### Static graph — matplotlib (`make run`)

After the simulation completes, a graph of the zone network is rendered using matplotlib:

- Each zone is drawn as a colored circle using the color from the map file.
- Zone names are printed inside the circle. Zones with `max_drones > 1` show a `max:N` label below.
- Connections are drawn as gray lines. Connections with `max_link_capacity > 1` show a `cap:N` label.
- A color legend in the top-right corner maps each color to its zone type.

This view is useful for understanding the map topology before or after running the simulation.

### Interactive animation — pygame (`make animate`)

An interactive window opens showing the drone routing network with live drone positions:

- **SPACE** — advance one turn and update drone positions on the graph.
- **Q** — close the window.

Drones are shown as orange circles with their ID label, positioned on top of their current zone. When a drone is in transit toward a restricted zone, it is rendered at the midpoint of the connection. Multiple drones on the same zone are spread out in a grid so they remain individually visible. Connection capacities and zone capacities are displayed as labels. A dynamic legend in the least-crowded corner shows zone colors and their types.

This mode is the most useful for understanding how the algorithm distributes drones and handles contention at bottleneck zones.

## Resources

### References

- [Dijkstra's algorithm — Wikipedia](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm)
- [flake8 documentation](https://flake8.pycqa.org/en/latest/)
- [mypy documentation](https://mypy.readthedocs.io/en/stable/)
- [colorama documentation](https://pypi.org/project/colorama/)
- [matplotlib documentation](https://matplotlib.org/stable/index.html)
- [pygame documentation](https://www.pygame.org/docs/)
- [PEP 257 — Docstring Conventions](https://peps.python.org/pep-0257/)

### Use of AI

AI (Claude by Anthropic and Gemini by Google) was used during the development of this project for the following tasks:

- Guidance on project structure and file organization
- Explanation of Dijkstra's algorithm and its application to weighted graphs with penalty-based diversification
- Help reviewing the simulation turn scheduling logic and capacity constraint enforcement
- Suggestions for the visual representation using matplotlib and pygame
- Review of type hints and mypy compliance
- Code review for conformance with the project specification

All generated code was reviewed, understood, tested, and adapted by the author before being included in the project. No code was blindly copied without understanding its purpose and behavior.

## License

This project was developed for educational purposes as part of the 42 curriculum.

## Author

Felipe José Hillebrand

GitHub: https://github.com/felipehillebrand-ops
