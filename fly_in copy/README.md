This project has been created as part of the 42 curriculum by **abougues**.

## Description

**Fly-in** is a drone simulation and a *Multi-Agent Path Finding (MAPF)* problem. The task is to route a set number of drones from a given map’s start to its end through a network of connected zones. The goal is simple: follow all movement and capacity constraints and finish in the least amount of turns possible!

This program parses a custom map file, builds a graph of zones and connections, calculates optimal paths using a weighted pathfinding algorithm with an iterative penalty-based diversification layer to prevent bottlenecks, and simulates the turn-by-turn movement of all drones. Movements are displayed directly via terminal output.

---

## Instructions

### Requirements
* `Python 3.10` or later
* `pip` or any compatible package manager

### Installation
make install

*Creates a virtual environment in `.venv/` and installs all dependencies from the `requirements.txt` file.*

### Run
```bash
    make run MAP=maps/easy/01_linear_path.txt
```
---

## Expected Map Format Example

```
nb_drones: 2
start_hub: launchpad 0 0 [color=green]
end_hub: helipad 3 0 [color=yellow]
hub: tunnelA 1 0 [zone=priority color=green max_drones=2]
hub: hallwayB 2 0 [zone=restricted color=red]
connection: launchpad-tunnelA
connection: tunnelA-hallwayB [max_link_capacity=2]
connection: hallwayB-helipad
```

### Zone Profile Reference

| Zone Type | Travel Cost | Behavior |
| :--- | :--- | :--- |
| **`normal`** | **1 turn** | Default baseline movement cost. |
| **`restricted`** | **2 turns** | Multi-turn travel (occupies the link during turn 1, lands on turn 2). |
| **`priority`** | **1 turn** | Equal travel cost to standard zones, but prioritized during route selection tie-breakers. |
| **`blocked`** | **INF (999 turns)** | Completely impassable terrain; auto-filtered by pathfinder. |

---

## Simulation Output Example
```bash
D1-tunnelA
D1-tunnelA-hallwayB D2-tunnelA
D1-hallwayB D2-tunnelA-hallwayB
D1-helipad D2-hallwayB
D2-helipad

Simulation complete!
  Total turns    : 5
  Drones landed  : 2
```

### Parsing Movement Syntax:
* `D1-tunnelA` $\rightarrow$ Standard 1-turn entry.
* `D1-tunnelA-hallwayB` $\rightarrow$ Turn 1 of entering a *restricted* zone (*in-transit*).
* `D1-hallwayB` $\rightarrow$ Turn 2 arrival at the target destination.

---

## How It Works

### 1. Pathfinder (`src/pathfinding.py`)
* Custom $O(V^2)$ **Dijkstra algorithm** built from scratch without external graph libraries.
* **Diversification Loop:** Runs up to 4 iterative Dijkstra passes per map. Each time a route is locked in, an artificial penalty multiplier ($1.5\times$) is applied to its intermediate hubs, forcing subsequent drones onto alternate routes to bypass bottlenecks.

### 2. Synced State Simulation (`src/simulation.py`)
Each tick processes movements through an evaluation chain:
* **Resolve In-Transit First:** Completes 2nd-turn movements for drones entering *restricted* zones.
* **Move Validation:** Enforces edge capacities (`max_link_capacity`) and node capacities (`max_drones`) while accounting for leaving vs. entering drones.
* **Deadlock Catching:** Raises `SimulationDeadlockError` if zero movements occur for 20 consecutive turns.

---

## Resources

* [Multi-Agent Path Finding - An Overview](https://www.researchgate.net/publication/336611576_Multi-Agent_Path_Finding_-_An_Overview)
* [Dijkstra Algorithm Visualization](https://gallery.selfboot.cn/en/algorithms/dijkstra)
* [GeeksforGeeks - Graph Data Structure](https://www.geeksforgeeks.org/dsa/graph-data-structure/)

---

## AI Usage

*AI (Claude by Anthropic)* was used in the planning phase of this project and its early planning phases for project structure, explanation and resource guidance, reviewing, and type hints aid. All usage of AI was understood, tested, and not heavily referenced.