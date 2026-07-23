from src.zone import Zone


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
