import sys
import time
from typing import Optional
import numpy as np
from .read_data import read_maze_data as read_m


def bin_maze(filepath: str) -> tuple:

    maze_lines, entry, ex, path_str = read_m(filepath)

    map_bits = np.array(
            [[int(char, 16) for char in line] for line in maze_lines])
    h, w = map_bits.shape

    grid = np.zeros((2 * h + 1, 2 * w + 1), dtype=np.uint8)
    grid[0::2, 0::2] = 1

    for r in range(h):
        for c in range(w):
            val = map_bits[r, c]
            cr, cc = 2 * r + 1, 2 * c + 1

            if val & 1:
                grid[cr - 1, cc] = 1
            if val & 2:
                grid[cr, cc + 1] = 1
            if val & 4:
                grid[cr + 1, cc] = 1
            if val & 8:
                grid[cr, cc - 1] = 1
    np.save("utilities/processed_map.npy", grid)

    return (int(entry[0]), int(entry[1])), (int(ex[0]), int(ex[1])), path_str


def terminal_display(entry: tuple[int, int],
                     exit_coord: tuple[int, int],
                     path_str: str,
                     path_color: Optional[int] = None,
                     wall_color: Optional[int] = None) -> None:
    c_start = "\033[92m"
    c_end = "\033[91m"
    c_reset = "\033[0m"

    if path_color is not None:
        pr = (path_color >> 16) & 255
        pg = (path_color >> 8) & 255
        pb = path_color & 255
        c_path = f"\033[38;2;{pr};{pg};{pb}m"
    else:
        c_path = "\033[93m"

    if wall_color is not None:
        wr = (wall_color >> 16) & 255
        wg = (wall_color >> 8) & 255
        wb = wall_color & 255
        c_wall = f"\033[38;2;{wr};{wg};{wb}m"
    else:
        c_wall = "\033[0m"

    bit_map = np.load("utilities/processed_map.npy")

    vis_grid = [
        [f"{c_wall}██{c_reset}" if cell == 1 else "  " for cell in row]
        for row in bit_map
    ]

    start_r, start_c = 2 * entry[1] + 1, 2 * entry[0] + 1
    end_r, end_c = 2 * exit_coord[1] + 1, 2 * exit_coord[0] + 1

    vis_grid[start_r][start_c] = f"{c_start}██{c_reset}"
    vis_grid[end_r][end_c] = f"{c_end}██{c_reset}"

    curr_r, curr_c = start_r, start_c
    moves = {'N': (-1, 0), 'S': (1, 0), 'E': (0, 1), 'W': (0, -1)}

    for move in path_str:
        dr, dc = moves.get(move, (0, 0))

        for _ in range(2):
            curr_r += dr
            curr_c += dc

            if vis_grid[curr_r][curr_c] == "  ":
                vis_grid[curr_r][curr_c] = f"{c_path}██{c_reset}"

        sys.stdout.write("\033[H")
        output = "\n".join("".join(row) for row in vis_grid)
        sys.stdout.write(output + "\n")
        sys.stdout.flush()

        time.sleep(0.05)


def dt(path_color: Optional[int] = None,
       wall_color: Optional[int] = None) -> None:
    entry, ex, path = bin_maze("utilities/maze_output.txt")
    terminal_display(entry, ex, path, path_color, wall_color)
