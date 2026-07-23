from src.zone import Zone, ZoneType
from src.connection import Connection


class Graph:
    """Represents the network of zones and connections."""

    def __init__(self) -> None:
        self.zones: list[Zone] = []
        self.connections: list[Connection] = []
        self.start: Zone | None = None
        self.end: Zone | None = None
        self.nb_drones: int = 0

    def add_zone(self, zone: Zone) -> None:
        """Add a zone to the graph."""
        if self.get_zone(zone.name) is not None:
            raise ValueError(
                f"Duplicate zone name: '{zone.name}'"
            )
        self.zones.append(zone)

    def add_connection(self, connection: Connection) -> None:
        """Add a connection to the graph."""
        self.connections.append(connection)

    def get_zone(self, name: str) -> Zone | None:
        """Return a zone by name, or None if not found."""
        for zone in self.zones:
            if zone.name == name:
                return zone
        return None

    def get_neighbors(self, zone: Zone) -> list[Zone]:
        """Return all zones directly connected to the given zone."""
        neighbors: list[Zone] = []
        for connection in self.connections:
            if connection.connects(zone):
                neighbor = connection.other(zone)
                if neighbor.zone_type != ZoneType.BLOCKED:
                    neighbors.append(neighbor)
        return neighbors

    def get_connection(self, zone_a: Zone, zone_b: Zone) -> Connection | None:
        """Return the connection between two zones, or None if not found."""
        for connection in self.connections:
            if connection.connects(zone_a) and connection.connects(zone_b):
                return connection
        return None
