#!/usr/bin/env python3

import sys
import structure as struc
from display import dt, md, bin_maze, random_color
from structure import MazeSolver

def main() -> None:
    print("=== A-Maze-Ing ===")
    print("\nParsing errors...")

    config_path = "utilities/config.txt"

    try:
        data = struc.validate_conf(config_path)
    except FileNotFoundError as e:
        print(f"Not the best path? - {e}")
        sys.exit(1)

    generator = struc.MazeGenerator(config_path)
    maze = generator.generate_maze(data, "basic")
    output_file = "utilities/maze_output.txt"
    entry = data['entry']
    exit_pos = data['exit']

    solver = MazeSolver(
        maze,
        entry,
        exit_pos
    )
    print("SOLVER WIDTH:", solver.width)
    print("SOLVER HEIGHT:", solver.height)
    print(
        "PHYSICAL:",
        max(x for x, y in maze) + 1,
        max(y for x, y in maze) + 1
    )
    solver.write_output("utilities/maze_output.txt")
    option = input("Terminal rendering (1) | MLX library (2) | exit(3): ")
    sys.stdout.write("\033[H")

    match option:
        case "1":
            solver.write_output("utilities/maze_output.txt")
            dt()
            while option != "3":
                option = input("Regen maze (1) | Change colour (2) | exit (3): ")
                sys.stdout.write("\033[H")
                match option:
                    case "1":
                        maze = generator.generate_maze(data, "basic")
                        dt()
                    case "2":
                        p_color = random_color()
                        w_color = random_color()
                        while p_color == w_color:
                            w_color = random_color()
                        dt(p_color, w_color)
                    case "3":
                        sys.exit("Exiting...")
                    case _:
                        sys.exit(1)
        case "2":
            entry, ex, path = bin_maze(output_file)
            md(entry, ex, path)
        case "3":
            sys.exit("Exiting...")
        case _:
            print("Error: Not a valid option")
            sys.exit(1)


if __name__ == "__main__":
    main()
