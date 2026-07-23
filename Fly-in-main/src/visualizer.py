import pygame
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from colorama import Fore, Style, init
from src.graph import Graph
from src.zone import ZoneType
from src.drone import Drone

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
            f"\n{Fore.GREEN}Simulation complete!{Style.RESET_ALL}"
        )
        print(
            f"  Total turns  : {Fore.YELLOW}{total_turns}{Style.RESET_ALL}"
        )
        print(
            f"  Drones delivered: "
            f"{Fore.YELLOW}{total_drones}{Style.RESET_ALL}"
        )

    def draw_graph(self, filepath: str = "") -> None:
        """Draw the graph using matplotlib."""
        fig, ax = plt.subplots(figsize=(15, 9))
        fig.patch.set_facecolor("#F3F3F3")
        ax.set_facecolor("white")

        map_name = filepath.split("/")[-1].replace(".txt", "")
        title = "Fly-in — Drone Routing Network"
        if map_name:
            title = f"Fly-in — {map_name} — Drone Routing Network"
        ax.set_title(title, fontsize=14, pad=25, color="black")
        ax.axis("off")
        ax.set_aspect("equal", adjustable="box")

        all_x = [z.x for z in self.graph.zones]
        all_y = [z.y for z in self.graph.zones]
        min_x, max_x = min(all_x), max(all_x)
        min_y, max_y = min(all_y), max(all_y)
        padding = 1.5

        ax.set_xlim(min_x - padding, max_x + padding)
        ax.set_ylim(min_y - padding, max_y + padding)

        mpl_colors: dict[str, str] = {
            "green": "#228B22",
            "red": "#C83232",
            "blue": "#3264C8",
            "yellow": "#DCB400",
            "gray": "#969696",
            "grey": "#969696",
            "orange": "#DC8200",
            "purple": "#9632C8",
            "cyan": "#00B4B4",
            "white": "#DCDCDC",
            "black": "#505050",
            "brown": "#8B5A2B",
            "lime": "#32C832",
            "magenta": "#C800C8",
            "gold": "#D2AA00",
            "pink": "#DC6496",
            "teal": "#009696",
            "maroon": "#800000",
            "darkred": "#8B0000",
            "violet": "#8A2BE2",
            "crimson": "#DC143C",
            "rainbow": "#9632C8",
            "none": "#6464C8",
        }

        for connection in self.graph.connections:
            ax.plot(
                [connection.zone_a.x, connection.zone_b.x],
                [connection.zone_a.y, connection.zone_b.y],
                color="#969696", linewidth=1.5, zorder=1
            )
            if connection.max_link_capacity > 1:
                mid_x = (connection.zone_a.x + connection.zone_b.x) / 2
                mid_y = (connection.zone_a.y + connection.zone_b.y) / 2
                ax.text(
                    mid_x, mid_y + 0.02,
                    f"cap:{connection.max_link_capacity}",
                    fontsize=7, ha="center", color="#820DFF"
                )

        seen_colors: dict[str, tuple[str, str]] = {}
        for zone in self.graph.zones:
            color = mpl_colors.get(zone.color, "#6464C8")
            if zone.color != "none" and zone.color not in seen_colors:
                seen_colors[zone.color] = (color, zone.zone_type.value)

            circle = mpatches.Circle(
                (zone.x, zone.y),
                0.25,
                facecolor=color,
                edgecolor="black",
                linewidth=1,
                zorder=2
            )
            ax.add_patch(circle)
            chars = 9
            short_name = zone.name[:chars]
            ax.text(
                zone.x, zone.y,
                short_name,
                fontsize=6,
                ha="center",
                va="center",
                color="black",
                fontweight="bold",
                zorder=3
            )
            if zone.max_drones > 1:
                ax.text(
                    zone.x, zone.y - 0.4,
                    f"max:{zone.max_drones}",
                    fontsize=7, ha="center", color="#112FDA"
                )

        legend_handles = [
            mpatches.Patch(
                color=color,
                label=f"{color_name} ({zone_type})"
            )
            for color_name, (color, zone_type) in seen_colors.items()
        ]
        if legend_handles:
            legend = ax.legend(
                handles=legend_handles,
                loc="upper left",
                bbox_to_anchor=(0.98, 1),
                borderaxespad=0,
                fontsize=10,
                facecolor="white",
                edgecolor="black",
                labelcolor="black",
                title="Colors",
                title_fontsize=10.5,
            )
            legend.get_title().set_color("black")

        plt.tight_layout()
        plt.show()

    def animate(
        self, drones: list[Drone], turn_log: list[str], filepath: str
    ) -> None:
        """
        Animate the simulation using pygame with precise transition logging.
        """
        pygame.init()

        width, height = 1200, 750
        screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Fly-in — Drone Routing Animation")
        clock = pygame.time.Clock()

        font = pygame.font.SysFont("monospace", 13, bold=True)
        font_small = pygame.font.SysFont("monospace", 11)
        font_title = pygame.font.SysFont("monospace", 16, bold=True)
        font_legend = pygame.font.SysFont("monospace", 16)
        font_drone = pygame.font.SysFont("monospace", 9, bold=True)

        all_x = [z.x for z in self.graph.zones]
        all_y = [z.y for z in self.graph.zones]
        min_x, max_x = min(all_x), max(all_x)
        min_y, max_y = min(all_y), max(all_y)
        margin = 100
        range_x = max_x - min_x or 1
        range_y = max_y - min_y or 1

        def to_screen(x: int, y: int) -> tuple[int, int]:
            """Convert graph coordinates to screen coordinates."""
            sx = int(margin + (x - min_x) / range_x * (width - 2 * margin))
            draw_height = height - 2 * margin - 100
            sy = int(50 + margin + (max_y - y) / range_y * draw_height)
            return sx, sy

        pygame_colors: dict[str, tuple[int, int, int]] = {
            "green": (34, 139, 34),
            "red": (200, 50, 50),
            "blue": (50, 100, 200),
            "yellow": (220, 180, 0),
            "gray": (150, 150, 150),
            "grey": (150, 150, 150),
            "orange": (220, 130, 0),
            "purple": (150, 50, 200),
            "cyan": (0, 180, 180),
            "white": (220, 220, 220),
            "black": (40, 40, 40),
            "brown": (139, 90, 43),
            "lime": (50, 200, 50),
            "magenta": (200, 0, 200),
            "gold": (210, 170, 0),
            "pink": (220, 100, 150),
            "teal": (0, 150, 150),
            "maroon": (128, 0, 0),
            "darkred": (139, 0, 0),
            "violet": (138, 43, 226),
            "crimson": (220, 20, 60),
            "rainbow": (150, 50, 200),
            "none": (100, 100, 200),
        }

        num_zones = len(self.graph.zones)
        radius = max(10, min(30, 600 // num_zones))
        map_name = filepath.split("/")[-1].replace(".txt", "")

        drone_positions: dict[str, str] = {
            f"D{d.drone_id}": self.graph.start.name
            for d in drones
            if self.graph.start
        }

        start_zone = self.graph.start
        assert start_zone is not None

        current_turn_idx = -1
        running = True
        bg_color = (20, 20, 30)

        def draw_legend() -> None:
            """Draw the zone color legend with zone types."""
            seen: dict[str, tuple[tuple[int, int, int], str]] = {}
            for zone in self.graph.zones:
                if zone.color != "none" and zone.color not in seen:
                    color = pygame_colors.get(zone.color, (100, 100, 200))
                    seen[zone.color] = (color, zone.zone_type.value)

            item_h = 20
            legend_w = 260
            legend_h = len(seen) * item_h + 30
            corners = [
                (25, height - legend_h - 10),
                (width - legend_w - 25, height - legend_h - 10),
                (25, 55),
                (width - legend_w - 25, 55),
            ]

            def corner_score(cx: int, cy: int) -> int:
                """Count how many zones are close to this corner."""
                score = 0
                for z in self.graph.zones:
                    zx, zy = to_screen(z.x, z.y)
                    if abs(zx - cx) < legend_w and abs(zy - cy) < legend_h:
                        score += 1
                return score

            best = min(corners, key=lambda c: corner_score(c[0], c[1]))
            lx, ly = best

            bg_surf = pygame.Surface((legend_w, legend_h), pygame.SRCALPHA)
            bg_surf.fill((0, 0, 0, 160))
            screen.blit(bg_surf, (lx - 5, ly - 5))

            pygame.draw.rect(
                screen, (255, 255, 255),
                (lx - 5, ly - 5, legend_w, legend_h), 1
            )

            label_title = font_legend.render("Colors:", True, (180, 180, 180))
            screen.blit(label_title, (lx, ly))
            ly += 22
            for color_name, (color_rgb, zone_type) in seen.items():
                pygame.draw.circle(screen, color_rgb, (lx + 7, ly + 7), 7)
                pygame.draw.circle(
                    screen, (255, 255, 255), (lx + 7, ly + 7), 7, 1
                    )
                text = font_legend.render(
                    f"{color_name} ({zone_type})", True, (200, 200, 200)
                )
                screen.blit(text, (lx + 20, ly))
                ly += item_h

        while running:
            screen.fill(bg_color)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if current_turn_idx < len(turn_log) - 1:
                            current_turn_idx += 1
                            for move in turn_log[current_turn_idx].split():
                                d_id, target = move.split("-", 1)
                                drone_positions[d_id] = target
                    elif event.key == pygame.K_q:
                        running = False

            turns_total = len(turn_log) if turn_log else 0
            curr_turn = current_turn_idx + 1 if current_turn_idx >= 0 else 0
            title_text = (
                f"Fly-in — {map_name} — Turn {curr_turn}/{turns_total}"
                f"  |  SPACE: next  |  Q: quit"
            )
            title_surf = font_title.render(title_text, True, (200, 200, 200))
            screen.blit(title_surf, (20, 15))

            for conn in self.graph.connections:
                p1 = to_screen(conn.zone_a.x, conn.zone_a.y)
                p2 = to_screen(conn.zone_b.x, conn.zone_b.y)
                pygame.draw.line(screen, (150, 150, 150), p1, p2, 2)

                if conn.max_link_capacity > 1:
                    mid_x = (p1[0] + p2[0]) // 2
                    mid_y = (p1[1] + p2[1]) // 2
                    cap_surf = font_small.render(
                        f"cap:{conn.max_link_capacity}", True, (200, 150, 255)
                    )
                    text_x = mid_x - cap_surf.get_width() // 2
                    text_y = mid_y - cap_surf.get_height() // 2 - 8
                    screen.blit(cap_surf, (text_x, text_y))

            for zone in self.graph.zones:
                pos = to_screen(zone.x, zone.y)
                color = pygame_colors.get(zone.color, (100, 100, 200))

                pygame.draw.circle(screen, color, pos, radius)
                pygame.draw.circle(screen, (255, 255, 255), pos, radius, 2)

                chars = max(4, radius // 2)
                label = font.render(zone.name[:chars], True, (255, 255, 255))
                screen.blit(label, (pos[0] - label.get_width() // 2,
                                    pos[1] - label.get_height() // 2))

                if zone.max_drones > 1:
                    max_surf = font_small.render(
                        f"max:{zone.max_drones}", True, (150, 220, 255)
                    )
                    screen.blit(max_surf, (pos[0] - max_surf.get_width() // 2,
                                           pos[1] + radius + 2))

            target_counts: dict[str, int] = {}
            for pos_str in drone_positions.values():
                target_counts[pos_str] = target_counts.get(pos_str, 0) + 1

            zone_counters: dict[str, int] = {}
            for d_id, pos_str in drone_positions.items():
                total_here = target_counts.get(pos_str, 1)

                if total_here <= 4:
                    drone_radius, spacing, max_cols = 10, 22, 2
                elif total_here <= 12:
                    drone_radius, spacing, max_cols = 7, 16, 3
                else:
                    drone_radius, spacing = 5, 12
                    max_cols = max(4, int(total_here ** 0.5) + 1)

                if "-" in pos_str:
                    parts = pos_str.split("-")
                    z_start = self.graph.get_zone(parts[0])
                    z_end = self.graph.get_zone(parts[-1])

                    if z_start is not None and z_end is not None:
                        p1 = to_screen(z_start.x, z_start.y)
                        p2 = to_screen(z_end.x, z_end.y)

                        drone_pos = (
                            (p1[0] + p2[0]) // 2,
                            (p1[1] + p2[1]) // 2
                        )
                    else:
                        drone_pos = to_screen(
                            start_zone.x,
                            start_zone.y
                        )
                else:
                    current_zone = self.graph.get_zone(pos_str)

                    if current_zone is None:
                        drone_pos = to_screen(
                            start_zone.x,
                            start_zone.y
                        )
                    else:
                        base_pos = to_screen(
                            current_zone.x,
                            current_zone.y
                        )
                        count = zone_counters.get(
                            current_zone.name,
                            0
                        )
                        zone_counters[current_zone.name] = count + 1

                        row = count // max_cols
                        col = count % max_cols

                        total_width = (min(total_here, max_cols) - 1) * spacing
                        x_shift = (col * spacing) - (total_width / 2)
                        y_shift = row * spacing + radius + drone_radius + 4

                        drone_pos = (
                            int(base_pos[0] + x_shift),
                            int(base_pos[1] - y_shift)
                        )

                pygame.draw.circle(
                    screen, (255, 120, 0), drone_pos, drone_radius
                )
                pygame.draw.circle(
                    screen, (255, 255, 255), drone_pos, drone_radius, 1
                )

                text_str = d_id if drone_radius >= 10 else d_id.replace(
                    "D", ""
                )

                if drone_radius >= 7:
                    d_num = font_drone.render(text_str, True, bg_color)
                    d_rect = d_num.get_rect(center=drone_pos)
                    screen.blit(d_num, d_rect)

            draw_legend()

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()
