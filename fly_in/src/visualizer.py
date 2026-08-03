import pygame
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from colorama import Fore, Style, init
from src.obj import Graph, ZoneType, Drone

init(autoreset=True)

ZONE_COLORS: dict[str, str] = {
    "green": "\033[32m",
    "blue": "\033[34m",
    "red": "\033[31m",
    "yellow": "\033[33m",
    "gray": "\033[37m",
    "grey": "\033[37m",
    "orange": "\033[38;5;208m",
    "purple": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[97m",
    "black": "\033[90m",
    "brown": "\033[38;5;130m",
    "lime": "\033[38;5;118m",
    "magenta": "\033[95m",
    "gold": "\033[38;5;220m",
    "pink": "\033[38;5;213m",
    "teal": "\033[38;5;30m",
    "maroon": "\033[38;5;88m",
    "darkred": "\033[38;5;124m",
    "violet": "\033[38;5;135m",
    "crimson": "\033[38;5;160m",
    "rainbow": "\033[38;5;201m",
    "none": "\033[37m",
}

ZONE_TYPE_COLORS: dict[ZoneType, str] = {
    ZoneType.NORMAL: "skyblue",
    ZoneType.PRIORITY: "blue",
    ZoneType.RESTRICTED: "red",
    ZoneType.BLOCKED: "gray",
}


class Visualizer:
    """Handles visual representation of the simulation."""

    def __init__(self, graph: Graph) -> None:
        self.graph = graph

    def print_turn(self, _turn: int, moves: str) -> None:
        """Print a simulation turn with colors in the terminal."""
        print(f"{Style.RESET_ALL}", end="")
        parts = moves.split()
        colored_parts = []
        print(f"\033[1mturn {_turn}: \033[22m", end="")
        for part in parts:
            drone_id, zone_name = part.split("-", 1)

            target_zone_name = zone_name
            if "-" in zone_name:
                target_zone_name = zone_name.split("-")[1]

            zone = self.graph.get_zone(target_zone_name)
            color = Fore.WHITE
            if zone is not None:
                color = ZONE_COLORS.get(zone.color, Fore.WHITE)

            colored_parts.append(
                f"{Fore.YELLOW}{drone_id}{Style.RESET_ALL}"
                f"-{color}{zone_name}{Style.RESET_ALL}"
            )
        print(" ".join(colored_parts))

    def print_summary(self, total_turns: int, total_drones: int) -> None:
        """Print a summary of the simulation results."""
        print(
            f"\n{Fore.GREEN}Simulation complete! All drones arrived "
            f"succesfully :D{Style.RESET_ALL}"
        )
        print(
            f"  Total nb of turns  : {Fore.YELLOW}{total_turns}"
            f"{Style.RESET_ALL}"
        )
        print(
            f"  Drones delivered: "
            f"{Fore.YELLOW}{total_drones}{Style.RESET_ALL}"
        )
