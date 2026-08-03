from typing import NoReturn
from src.obj import Zone, ZoneType, Connection, Drone
from src.obj import Graph


class Map:

    """
    Mandatory Map class containing map info such as number of drones,
    zones and their cnncts.
    """

    def __init__(self, nb_drones: int = 0,
                 cnncts: list[Connection] | None = None,
                 zones: dict[str, Zone] | None = None,
                 drones: list[Drone] | None = None) -> None:
        self.nb_drones: int = nb_drones
        self.cnncts: list[Connection] = cnncts if cnncts is not None else [
        ]
        self.zones: dict[str, Zone] = zones if zones is not None else {}
        self.drones: list[Drone] = drones if drones is not None else []

    def add_connection(self, link: Connection) -> None:
        """Add a connection to this map."""
        self.cnncts.append(link)


class Parser:
    """
    Parses the input map file and builds a Graph object
    """

    def __init__(self) -> None:
        self.current_line = 0

    def error(self, msg: str) -> NoReturn:
        """Raise a parsing error with the current line number attached."""
        raise ValueError(f"{msg} on line {self.current_line} \u274c")

    # -----------------------------------
    def get_metadata(self, line: str) -> tuple[str, str | None]:
        if "[" in line:
            base, _, content = line.rpartition("[")
            content = content.strip("]")
            return base, content
        return line, None

    # -----------------------------------
    def hub_parser(self, line: str) -> tuple[str, Zone]:
        try:
            hub_type, info = line.split(":", 1)
        except ValueError:
            self.error(f"Invalid hub format, missing ':' in '{line}'")

        metadata: list[str] = []
        info, tags = self.get_metadata(info)
        if tags:
            tags = self._normalize_zone_tags(tags)
            metadata = tags.split()

        name_x_y = info.split()

        if len(name_x_y) > 3:
            self.error(f"Too many values given in '{line}'")

        try:
            name = name_x_y[0]
            x = int(name_x_y[1])
            y = int(name_x_y[2])
        except IndexError:
            self.error(f"Missing name, x, or y in '{line}'")
        except (ValueError, TypeError):
            self.error(f"x and y must be integers in '{line}'")

        if "-" in name:
            self.error(f"zone name cannot contain dashes -> '{name}'")

        zone_type = ZoneType.NORMAL
        color = "none"
        max_drones = 1

        for i in metadata:
            try:
                key, value = i.split("=")
            except ValueError:
                self.error(f"Metadata tag '{i}' must "
                           "follow 'key=value' format")

            if key == "color":
                color = value
            elif key == "max_drones":
                try:
                    max_drones = int(value)
                except ValueError:
                    self.error("'max_drones' must be an integer, "
                               f"got '{value}'")
                if max_drones <= 0:
                    self.error(f"'max_drones' must be positive, got '{value}'")
            elif key == "zone":
                valid_types = [z.value for z in ZoneType]
                if value not in valid_types:
                    self.error(f"Invalid zone type '{value}', must be one of "
                               f"{valid_types} (line {line})")
                zone_type = ZoneType(value)
            else:
                self.error(f"Unknown metadata key: '{key}'")

        zone = Zone(name, x, y, zone_type, color, max_drones)
        return hub_type, zone

    @staticmethod
    def _normalize_zone_tags(tags: str) -> str:
        """Accept the legacy 'zone restricted' (space) shorthand alongside
        the standard 'zone=restricted' form, by rewriting it before the
        tags string gets split into individual key=value tokens."""
        for zt in ZoneType:
            tags = tags.replace(f"zone {zt.value}", f"zone={zt.value}")
        return tags

    # -----------------------------------
    def connect_parse(self, line: str, graph: "Graph") -> None:
        try:
            _, content = line.split(":", 1)
        except ValueError:
            self.error(f"Invalid connection format, missing ':' in '{line}'")

        clean_text, tags = self.get_metadata(content)

        if "-" not in clean_text:
            self.error("Connections need a '-' between zone names in"
                       f"'{line}'")

        try:
            n1, n2 = clean_text.split("-")
            n1, n2 = n1.strip(), n2.strip()
        except ValueError:
            self.error(f"Invalid connection format in '{line}'")

        zone_a = graph.get_zone(n1)
        zone_b = graph.get_zone(n2)

        if zone_a is None or zone_b is None:
            missing = n1 if zone_a is None else n2
            self.error(f"Zone '{missing}' does not exist")

        if graph.get_connection(zone_a, zone_b) is not None:
            self.error(f"Duplicate connection between '{n1}' and '{n2}'")

        tags_dict = dict(t.split("=") for t in tags.split()) if tags else {}

        try:
            max_link = int(tags_dict.get("max_link_capacity", 1))
        except ValueError:
            self.error(f"'max_link_capacity' must be an integer in '{line}'")
        if max_link <= 0:
            self.error(f"'max_link_capacity' must be positive in '{line}'")

        connection = Connection(zone_a, zone_b, max_link)
        graph.add_connection(connection)

    # -----------------------------------
    def parse_file(self, the_file: str) -> "Graph":
        graph = Graph()
        seen_nb_drones = False

        try:
            with open(the_file, "r") as f:
                lines = f.readlines()
        except FileNotFoundError:
            raise FileNotFoundError(f"Map file not found: {the_file}")

        first_active_line = True
        for raw_line in lines:
            self.current_line += 1
            line = raw_line.strip()

            if not line or line.startswith("#"):
                continue

            if first_active_line:
                first_active_line = False
                if not line.startswith("nb_drones:"):
                    self.error(
                        "the first active line must define 'nb_drones:'"
                    )

            if line.startswith("nb_drones:"):
                if seen_nb_drones:
                    self.error(
                        "'nb_drones' must exclusively be defined once "
                        "at the top"
                    )
                try:
                    graph.nb_drones = int(line.split(":")[1].strip())
                except (IndexError, ValueError):
                    self.error("'nb_drones' must be an integer")
                if graph.nb_drones <= 0:
                    self.error("'nb_drones' must be positive")
                seen_nb_drones = True

            elif "hub:" in line:
                hub_type, zone = self.hub_parser(line)
                if graph.get_zone(zone.name) is not None:
                    self.error(f"Duplicate zone name '{zone.name}'")

                if hub_type == "start_hub":
                    if graph.start is not None:
                        self.error("multiple start_hub definitions found")
                    graph.start = zone
                elif hub_type == "end_hub":
                    if graph.end is not None:
                        self.error("multiple end_hub definitions found")
                    graph.end = zone

                graph.add_zone(zone)

            elif line.startswith("connection:"):
                self.connect_parse(line, graph)

            else:
                self.error(f"unknown prefix -> '{line}'")

        if graph.nb_drones == 0:
            self.error("Missing 'nb_drones' definition in file")
        if graph.start is None:
            self.error("Missing 'start_hub' definition in file")
        if graph.end is None:
            self.error("Missing 'end_hub' definition in file")

        return graph
