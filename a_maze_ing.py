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
    try:
        struc.validate_maze(struc.generate_maze(), data)
    except FileNotFoundError as e:
        print(f"Not the best path? - {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
