#!/usr/bin/env python3

import structure as struc
import sys


def main() -> None:
    print("=== A-Maze-Ing ===")
    print("\nParsing errors...")
    try:
        data = struc.validate_conf("utilities/config.txt")
    except FileNotFoundError as e:
        print(f"Not the best path? - {e}")
        sys.exit(1)
    with open(struc.generate_maze(data), 'r', encoding='utf-8') as file:
            raw_data = [line.strip() for line in file]

    while True:
        match input("Terminal rendering (1) | MLX library (2) | MLX 3D (3) | exit(4)"):
            case 1:
                print()
            case 2:
                print()
            case 3:
                print()
            case 4:
                sys.exit("Exiting...")
            case _:
                raise ValueError("Not a valid option")


if __name__ == "__main__":
    main()
