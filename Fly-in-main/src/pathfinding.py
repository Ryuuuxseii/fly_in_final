from src.zone import Zone, ZoneType
from src.graph import Graph


class Pathfinder:
    """Finds shortest paths in a Graph using Dijkstra's algorithm."""

    def __init__(self, graph: Graph) -> None:
        self.graph = graph

    def _path_weight(self, zone: Zone, penalties: dict[str, float]) -> float:
        """
        Return the pathfinding weight for a zone, including dynamic penalties.

        Priority zones cost 1 turn (same as normal zones) but are preferred
        when two routes tie: the tiebreaker in zone selection gives priority
        zones a lower sort key so Dijkstra expands them first.
        Penalties are added dynamically to force alternative route exploration.
        """
        weights: dict[ZoneType, float] = {
            ZoneType.PRIORITY: 1.0,
            ZoneType.NORMAL: 1.0,
            ZoneType.RESTRICTED: 2.0,
            ZoneType.BLOCKED: 999.0,
        }
        return weights[zone.zone_type] + penalties.get(zone.name, 0.0)

    def find_path(
        self, start: Zone, end: Zone, penalties: dict[str, float]
    ) -> list[Zone]:
        """
        Find the shortest path from start to end using Dijkstra with penalties.
        """
        distances: dict[str, float] = {
            zone.name: float("inf") for zone in self.graph.zones
        }
        previous: dict[str, Zone | None] = {
            zone.name: None for zone in self.graph.zones
        }
        distances[start.name] = 0.0
        unvisited: list[Zone] = [
            z for z in self.graph.zones
            if z.zone_type != ZoneType.BLOCKED
        ]

        def sort_key(zone: Zone) -> tuple[float, int]:
            tiebreaker = 0 if zone.zone_type == ZoneType.PRIORITY else 1
            return (distances[zone.name], tiebreaker)

        while unvisited:
            current = min(unvisited, key=sort_key)

            if distances[current.name] == float("inf"):
                break

            if current == end:
                break

            unvisited.remove(current)

            for neighbor in self.graph.get_neighbors(current):
                cost = self._path_weight(neighbor, penalties)
                new_dist = distances[current.name] + cost

                if new_dist < distances[neighbor.name]:
                    distances[neighbor.name] = new_dist
                    previous[neighbor.name] = current

                elif (
                    new_dist == distances[neighbor.name]
                    and neighbor.zone_type == ZoneType.PRIORITY
                ):
                    previous[neighbor.name] = current

        return self._reconstruct_path(start, end, previous)

    def _reconstruct_path(
        self,
        start: Zone,
        end: Zone,
        previous: dict[str, Zone | None]
    ) -> list[Zone]:
        """Reconstruct the path from start to end using the previous map."""
        path: list[Zone] = []
        current: Zone | None = end

        while current is not None:
            path.append(current)
            current = previous[current.name]

        path.reverse()

        if not path or path[0] != start:
            return []

        return path

    def find_all_paths_dijkstra_penalty(
        self, start: Zone, end: Zone, max_paths: int = 10
    ) -> list[list[Zone]]:
        """
        Find up to max_paths diverse paths using Iterative
        Dijkstra with Penalties.

        Returns a list of high-quality distinct paths tailored
        to avoid bottlenecks.
        """
        all_paths: list[list[Zone]] = []
        penalties: dict[str, float] = {
            zone.name: 0.0 for zone in self.graph.zones
        }

        for _ in range(max_paths):
            path = self.find_path(start, end, penalties)
            if not path:
                break
            all_paths.append(path)

            for zone in path[1:-1]:
                penalties[zone.name] += 1.5

        return all_paths
