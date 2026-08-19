#!/usr/bin/env python3

import sys

import structure as struc
from display import dt, md, bin_maze, random_color
from structure import MazeSolver
from mazegen import MazeGenerator


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
        data = struc.validate_conf(sys.argv[1])
    except FileNotFoundError as e:
        print(f"Not the best path? - {e}")
        sys.exit(1)
    except SyntaxError:
        sys.exit("Syntax Error")
    except OSError:
        sys.exit("OS Error")
    except ValueError:
        sys.exit("Value Error")

    sys.stdout.write("\033[H\033[J")
    try:
        generator = create_generator(data)
        maze = generator.generate()
    except ValueError as e:
        sys.exit(e)

    entry = generator.get_entry
    exit_pos = generator.get_exit

    solver = MazeSolver(
        maze,
        entry,
        exit_pos,
    )

    solver.write_output(data['output_file'])

    option = input(
        "Terminal rendering (1) | MLX library (2) | exit(3): "
    )
    sys.stdout.write("\033[H")

    match option:
        case "1":
            solver.write_output(data['output_file'])
            dt(data["output_file"])

            while option != "3":
                option = input(
                    "Regen maze (1)"
                    "| Change colour (2) | exit (3): "
                )
                sys.stdout.write("\033[H")

                match option:
                    case "1":
                        if data['seed'] == 0:
                            maze = generator.generate()
                            solver = MazeSolver(maze, entry, exit_pos)
                            solver.write_output(data['output_file'])
                        dt(data["output_file"])

                    case "2":
                        p_color = random_color()
                        w_color = random_color()

                        while p_color == w_color:
                            w_color = random_color()

                        dt(data["output_file"], p_color, w_color)

                    case "3":
                        sys.exit(0)

                    case _:
                        sys.exit("Not a valid option")

        case "2":
            entry, ex, path = bin_maze(data['output_file'])
            md(entry, ex, path, sys.argv[1])

        case "3":
            sys.exit(0)

        case _:
            sys.stdout.write("\033[H\033[J")
            sys.exit("Error: Not a valid option")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
