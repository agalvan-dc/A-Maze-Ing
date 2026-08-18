#!/usr/bin/env python3

import sys

import structure as struc
from display import dt, md, bin_maze, random_color
from structure import MazeSolver
from mazegen import MazeGenerator


CONFIG_PATH = "utilities/config.txt"
OUTPUT_FILE = "utilities/maze_output.txt"


def create_generator(data: dict) -> MazeGenerator:
    """Create a reusable maze generator from the parsed configuration."""
    seed = data["seed"]

    if seed == "" or seed == "random" or seed == "RANDOM":
        seed = None

    perfect = data["perfect"]

    if isinstance(perfect, str):
        perfect = perfect == "True"

    return MazeGenerator(
        width=int(data["width"]),
        height=int(data["height"]),
        seed=seed,
        entry=tuple(data["entry"]),
        exit=tuple(data["exit"]),
        perfect=perfect,
    )


def main() -> None:
    print("=== A-Maze-Ing ===")
    print("\nParsing errors...")

    try:
        data = struc.validate_conf(CONFIG_PATH)
    except FileNotFoundError as e:
        print(f"Not the best path? - {e}")
        sys.exit(1)

    generator = create_generator(data)
    maze = generator.generate()

    entry = data["entry"]
    exit_pos = data["exit"]

    solver = MazeSolver(
        maze,
        entry,
        exit_pos,
    )

    print("SOLVER WIDTH:", solver.width)
    print("SOLVER HEIGHT:", solver.height)
    print(
        "PHYSICAL:",
        max(x for x, y in maze) + 1,
        max(y for x, y in maze) + 1,
    )

    solver.write_output(OUTPUT_FILE)

    option = input(
        "Terminal rendering (1) | MLX library (2) | exit(3): "
    )
    sys.stdout.write("\033[H")

    match option:
        case "1":
            solver.write_output(OUTPUT_FILE)
            dt()

            while option != "3":
                option = input(
                    "Regen maze (1)"
                    "| Change colour (2) | exit (3): "
                )
                sys.stdout.write("\033[H")

                match option:
                    case "1":
                        maze = generator.generate()
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
            entry, ex, path = bin_maze(OUTPUT_FILE)
            md(entry, ex, path)

        case "3":
            sys.exit("Exiting...")

        case _:
            print("Error: Not a valid option")
            sys.exit(1)


if __name__ == "__main__":
    main()
