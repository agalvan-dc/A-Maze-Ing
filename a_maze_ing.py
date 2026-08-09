#!/usr/bin/env python3

import sys
import structure as struc
from display import dt, md, bin_maze

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
    generator.generate_maze(data, "basic")
    
    output_file = "utilities/maze_output.txt"
    opcion = input("Terminal rendering (1) | MLX library (2) | exit(3): ")
    
    match opcion:
        case "1":
            dt()
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
