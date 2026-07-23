import re
from src.zone import Zone, ZoneType
from src.connection import Connection
from src.graph import Graph


class Parser:
    """Parses the input map file and builds a Graph object."""
    def parse_file(self, filepath: str) -> Graph:
        """Parse a map file and return a populated Graph."""
        graph = Graph()
        try:
            with open(filepath, "r") as f:
                lines = f.readlines()
        except FileNotFoundError:
            raise FileNotFoundError(f"Map file not found: {filepath}")

        for i, line in enumerate(lines, start=1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            self._parse_line(line, i, graph)

        self._validate_graph(graph)
        return graph

    def _parse_line(self, line: str, lineno: int, graph: Graph) -> None:
        """Parse a single line and update the graph accordingly."""
        if graph.nb_drones == 0 and not line.startswith("nb_drones:"):
            raise SyntaxError(
                f"Line {lineno}: the first active line must define "
                "'nb_drones:'"
            )
        if line.startswith("nb_drones:"):
            if graph.nb_drones != 0:
                raise SyntaxError(
                    f"Line {lineno}: 'nb_drones' must exclusively be "
                    "defined once at the top"
                )
            graph.nb_drones = self._parse_nb_drones(line, lineno)
        elif line.startswith("start_hub:"):
            if graph.start is not None:
                raise SyntaxError(
                    f"Line {lineno}: multiple start_hub definitions found"
                )
            zone = self._parse_zone(line, lineno)
            try:
                graph.add_zone(zone)
            except ValueError:
                raise SyntaxError(
                    f"Line {lineno}: duplicate zone name -> '{zone.name}'"
                )
            graph.start = zone
        elif line.startswith("end_hub:"):
            if graph.end is not None:
                raise SyntaxError(
                    f"Line {lineno}: multiple end_hub definitions found"
                )
            zone = self._parse_zone(line, lineno)
            try:
                graph.add_zone(zone)
            except ValueError:
                raise SyntaxError(
                    f"Line {lineno}: duplicate zone name -> '{zone.name}'"
                )
            graph.end = zone
        elif line.startswith("hub:"):
            zone = self._parse_zone(line, lineno)
            try:
                graph.add_zone(zone)
            except ValueError:
                raise SyntaxError(
                    f"Line {lineno}: duplicate zone name -> '{zone.name}'"
                )
        elif line.startswith("connection:"):
            graph.add_connection(self._parse_connection(line, lineno, graph))
        else:
            raise SyntaxError(f"Line {lineno}: unknown prefix -> '{line}'")

    def _parse_nb_drones(self, line: str, lineno: int) -> int:
        """Parse the nb_drones line and return the number of drones."""
        parts = line.split(":")
        try:
            value = int(parts[1].strip())
            if value <= 0:
                raise ValueError
            return value
        except (IndexError, ValueError):
            raise SyntaxError(
                f"Line {lineno}: invalid nb_drones value -> '{line}'"
            )

    def _parse_zone(self, line: str, lineno: int) -> Zone:
        """Parse a hub/start_hub/end_hub line and return a Zone object."""
        pattern = r"^(start_hub|end_hub|hub):\s+(\S+)\s+(-?\d+)\s+(-?\d+)"
        match = re.match(pattern, line)
        if not match:
            raise SyntaxError(
                f"Line {lineno}: invalid zone definition -> '{line}'"
            )

        name = match.group(2)
        x = int(match.group(3))
        y = int(match.group(4))

        meta_match = re.search(r"\[(.+)\]", line)
        end_pos = meta_match.start() if meta_match else len(line)
        rest = line[match.end():end_pos]
        if rest.strip():
            raise SyntaxError(
                f"Line {lineno}: invalid zone definition -> '{line}'"
            )

        if "-" in name:
            raise SyntaxError(
                f"Line {lineno}: zone name cannot contain dashes -> '{name}'"
            )

        metadata = self._parse_metadata(line, lineno)
        zone_type = self._parse_zone_type(metadata.get("zone", "normal"),
                                          lineno)
        color = metadata.get("color", "none")
        max_drones = self._parse_capacity(
            metadata.get("max_drones", "1"), lineno
        )

        return Zone(name, x, y, zone_type, color, max_drones)

    def _parse_connection(
        self, line: str, lineno: int, graph: Graph
    ) -> Connection:
        """Parse a connection line and return a Connection object."""
        pattern = r"^connection:\s+(\S+)-(\S+)"
        match = re.match(pattern, line)
        if not match:
            raise SyntaxError(
                f"Line {lineno}: invalid connection definition -> '{line}'"
            )

        name_a = match.group(1)
        name_b = match.group(2)

        zone_a = graph.get_zone(name_a)
        zone_b = graph.get_zone(name_b)

        if zone_a is None:
            raise SyntaxError(
                f"Line {lineno}: unknown zone '{name_a}'"
            )
        if zone_b is None:
            raise SyntaxError(
                f"Line {lineno}: unknown zone '{name_b}'"
            )

        if graph.get_connection(zone_a, zone_b) is not None:
            raise SyntaxError(
                f"Line {lineno}: duplicate connection "
                f"'{name_a}-{name_b}'"
            )

        metadata = self._parse_metadata(line, lineno)
        max_link_capacity = self._parse_capacity(
            metadata.get("max_link_capacity", "1"), lineno
        )
        return Connection(zone_a, zone_b, max_link_capacity)

    def _parse_metadata(self, line: str, lineno: int) -> dict[str, str]:
        """Extract metadata from brackets and return as a dictionary."""
        metadata: dict[str, str] = {}
        match = re.search(r"\[(.+)\]", line)

        if not match:
            return metadata

        content = match.group(1).strip()
        content = re.sub(r"zone\s+restricted", "zone=restricted", content)
        content = re.sub(r"zone\s+priority", "zone=priority", content)
        content = re.sub(r"zone\s+normal", "zone=normal", content)
        content = re.sub(r"zone\s+blocked", "zone=blocked", content)

        for pair in content.split():
            if "=" not in pair:
                raise SyntaxError(
                    f"Line {lineno}: invalid metadata format -> '{pair}'"
                )
            key, value = pair.split("=", 1)
            metadata[key.strip()] = value.strip()
        return metadata

    def _parse_zone_type(self, value: str, lineno: int) -> ZoneType:
        """Parse and validate a zone type string."""
        try:
            return ZoneType(value)
        except ValueError:
            raise SyntaxError(
                f"Line {lineno}: invalid zone type '{value}'"
            )

    def _parse_capacity(self, value: str, lineno: int) -> int:
        """Parse and validate a capacity value."""
        try:
            capacity = int(value)
            if capacity <= 0:
                raise ValueError
            return capacity
        except ValueError:
            raise SyntaxError(
                f"Line {lineno}: capacity must be a positive integer "
                f"and greater than zero -> '{value}'"
            )

    def _validate_graph(self, graph: Graph) -> None:
        """Validate that the graph has all required components."""
        if graph.nb_drones == 0:
            raise SyntaxError("Missing nb_drones definition")
        if graph.start is None:
            raise SyntaxError("Missing start_hub definition")
        if graph.end is None:
            raise SyntaxError("Missing end_hub definition")
