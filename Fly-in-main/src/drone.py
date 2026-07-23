from src.zone import Zone
from src.connection import Connection


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
