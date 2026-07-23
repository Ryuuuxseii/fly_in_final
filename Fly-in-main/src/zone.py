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
