import sys
import traceback
from src.parser import Parser
from src.simulation import Simulation, SimulationDeadlockError
from src.visualizer import Visualizer


def main() -> None:
    """Entry point for the Fly-in drone routing simulation."""
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python3 src/main.py <map_file> [--static|--animate]")
        sys.exit(1)

    filepath = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) == 3 else "--static"

    if mode not in ("--static", "--animate"):
        print("Error: mode must be --static or --animate")
        sys.exit(1)

    try:
        parser = Parser()
        graph = parser.parse_file(filepath)
        visualizer = Visualizer(graph)
        simulation = Simulation(graph)
        turn_log = simulation.run()

        for i, line in enumerate(turn_log, start=1):
            visualizer.print_turn(i, line)

        visualizer.print_summary(len(turn_log), graph.nb_drones)

        if mode == "--static":
            visualizer.draw_graph(filepath)
        else:
            visualizer.animate(simulation.drones, turn_log, filepath)

    except (FileNotFoundError, SyntaxError, ValueError,
            SimulationDeadlockError) as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        tb = traceback.extract_tb(e.__traceback__)
        print(f"Failed on the function: {tb[-1].name}")
        print(f"{type(e).__name__}: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
