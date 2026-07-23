from src.drone import Drone
from src.graph import Graph
from src.pathfinding import Pathfinder
from src.zone import Zone, ZoneType


class SimulationDeadlockError(Exception):
    """
    Custom exception raised when simulation enters an unrecoverable deadlock.
    """
    pass


class Simulation:
    """Manages the drone routing simulation turn by turn synchronously."""

    def __init__(self, graph: Graph) -> None:
        self.graph = graph
        self.pathfinder = Pathfinder(graph)
        self.drones: list[Drone] = []
        self.turn_log: list[str] = []
        self._initialize_drones()

    def _initialize_drones(self) -> None:
        """Create all drones and assign paths using multiple routes."""
        if self.graph.start is None or self.graph.end is None:
            raise ValueError("Graph must have a start and end zone")

        target_max_paths = 2 if self.graph.nb_drones >= 25 else 4

        all_paths = self.pathfinder.find_all_paths_dijkstra_penalty(
            self.graph.start, self.graph.end, max_paths=target_max_paths
        )

        if not all_paths:
            raise ValueError("No valid path found from start to end")

        for i in range(1, self.graph.nb_drones + 1):
            drone = Drone(i, self.graph.start)
            chosen_path = all_paths[(i - 1) % len(all_paths)]
            drone.path = list(chosen_path[1:])
            self.drones.append(drone)

    def run(self) -> list[str]:
        """Run the simulation and return the turn log with deadlock safety."""
        MAX_STALL_TURNS = 20
        stall_turns = 0

        while not self._all_delivered():
            moved = self._run_turn()

            if moved:
                stall_turns = 0
            else:
                stall_turns += 1
                if stall_turns >= MAX_STALL_TURNS:
                    raise SimulationDeadlockError(
                        f"Simulation deadlock detected: no drone moved "
                        f"for {MAX_STALL_TURNS} consecutive turns."
                    )

        return self.turn_log

    def _all_delivered(self) -> bool:
        """Check if all drones have been delivered."""
        return all(drone.delivered for drone in self.drones)

    def _run_turn(self) -> bool:
        """Execute one simulation turn synchronously."""
        moves: list[str] = []
        entering: list[Zone] = []
        leaving: list[Zone] = []
        conn_usage: dict[str, int] = {}
        drones_acted: set[Drone] = set()
        start_occupants: dict[str, int] = {}

        for d in self.drones:
            if not d.delivered and not d.in_transit:
                zname = d.current_zone.name
                start_occupants[zname] = start_occupants.get(zname, 0) + 1

        for drone in self.drones:
            if drone.delivered or not drone.in_transit:
                continue

            dest = drone.transit_destination
            if dest is None:
                continue

            if dest != self.graph.end:
                current_occupants = start_occupants.get(dest.name, 0)
                already_arriving = sum(
                    1 for z in entering if z == dest
                )
                if (current_occupants + already_arriving
                        >= dest.max_drones):
                    continue

            entering.append(dest)
            drone.current_zone = dest
            drone.in_transit = False
            drone.transit_connection = None
            drone.transit_destination = None
            moves.append(f"{drone}-{dest.name}")
            drones_acted.add(drone)

            if dest == self.graph.end:
                drone.delivered = True

        candidates: list[Drone] = []
        for drone in self.drones:
            if drone.delivered or drone.in_transit or drone in drones_acted:
                continue
            if not drone.path:
                continue
            next_zone = drone.path[0]
            if self.graph.get_connection(drone.current_zone, next_zone):
                leaving.append(drone.current_zone)
                candidates.append(drone)

        for drone in candidates:
            next_zone = drone.path[0]

            if not self._can_move(
                drone,
                next_zone,
                entering,
                leaving,
                conn_usage,
                start_occupants
            ):
                leaving.remove(drone.current_zone)
                continue

            conn = self.graph.get_connection(drone.current_zone, next_zone)
            if conn is None:
                leaving.remove(drone.current_zone)
                continue

            conn_key = self._conn_key(drone.current_zone, next_zone)
            conn_usage[conn_key] = conn_usage.get(conn_key, 0) + 1

            if next_zone.zone_type == ZoneType.RESTRICTED:
                drone.in_transit = True
                drone.transit_connection = conn
                drone.transit_destination = next_zone
                drone.path.pop(0)
                conn_label = f"{drone.current_zone.name}-{next_zone.name}"
                moves.append(f"{drone}-{conn_label}")
            else:
                entering.append(next_zone)
                drone.path.pop(0)
                drone.current_zone = next_zone
                moves.append(f"{drone}-{next_zone.name}")

                if next_zone == self.graph.end:
                    drone.delivered = True

        if moves:
            self.turn_log.append(" ".join(moves))

        return len(moves) > 0

    def _conn_key(self, zone_a: Zone, zone_b: Zone) -> str:
        """Return a canonical key for a connection (order-independent)."""
        names = sorted([zone_a.name, zone_b.name])
        return f"{names[0]}-{names[1]}"

    def _can_move(
        self,
        drone: Drone,
        next_zone: Zone,
        entering: list[Zone],
        leaving: list[Zone],
        conn_usage: dict[str, int],
        start_occupants: dict[str, int],
    ) -> bool:
        """Check if a drone can move to next_zone this turn."""
        conn = self.graph.get_connection(drone.current_zone, next_zone)
        if conn is None:
            return False

        conn_key = self._conn_key(drone.current_zone, next_zone)
        if conn_usage.get(conn_key, 0) >= conn.max_link_capacity:
            return False

        if next_zone == self.graph.end or next_zone == self.graph.start:
            return True

        current_occupants = start_occupants.get(next_zone.name, 0)

        leaving_count = sum(1 for z in leaving if z == next_zone)
        entering_count = sum(1 for z in entering if z == next_zone)

        if next_zone.zone_type == ZoneType.RESTRICTED:
            in_transit_future = sum(
                1 for d in self.drones
                if d.transit_destination == next_zone
                and d != drone
                and d.in_transit
            )
            effective = (
                current_occupants
                - leaving_count
                + entering_count
                + in_transit_future
            )
        else:
            effective = current_occupants - leaving_count + entering_count

        return effective < next_zone.max_drones
