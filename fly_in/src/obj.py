from enum import Enum


class ZoneType(Enum):
    """Enum representing the possible types of a zone."""

    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"

    def cost(self) -> int:
        """Return the movement cost for this zone type."""
        costs = {
            ZoneType.NORMAL: 1,
            ZoneType.PRIORITY: 1,
            ZoneType.RESTRICTED: 2,
            ZoneType.BLOCKED: 999,
        }
        return costs[self]


class Zone:
    """Represents a zone (node) in the drone routing network."""

    def __init__(
        self,
        name: str,
        x: int,
        y: int,
        zone_type: ZoneType = ZoneType.NORMAL,
        color: str = "none",
        max_drones: int = 1,
    ) -> None:
        self.name = name
        self.x = x
        self.y = y
        self.zone_type = zone_type
        self.color = color
        self.max_drones = max_drones


class Connection:
    """Represents a bidirectional connection (edge) between two zones."""

    def __init__(
        self,
        zone_a: Zone,
        zone_b: Zone,
        max_link_capacity: int = 1,
    ) -> None:
        self.zone_a = zone_a
        self.zone_b = zone_b
        self.max_link_capacity = max_link_capacity

    def connects(self, zone: Zone) -> bool:
        """Check if this connection involves the given zone."""
        return zone == self.zone_a or zone == self.zone_b

    def other(self, zone: Zone) -> Zone:
        """Return the other zone in the connection."""
        if zone == self.zone_a:
            return self.zone_b
        return self.zone_a


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


class Drone:
    """Represents a drone in the simulation."""

    def __init__(self, drone_id: int, start: Zone) -> None:
        self.drone_id = drone_id
        self.current_zone: Zone = start
        self.path: list[Zone] = []
        self.delivered: bool = False
        self.in_transit: bool = False
        self.transit_connection: Connection | None = None
        self.transit_destination: Zone | None = None

    def __str__(self) -> str:
        """Return the drone identifier string."""
        return f"D{self.drone_id}"
