import numpy as np
import os
import time
import subprocess
from .read_data import read_maze_data as read_m


def bin_maze(filepath: str) -> tuple:

    maze_lines, entry, ex, path_str = read_m(filepath)

    map_bits = np.array(
            [[int(char, 16) for char in line.strip()] for line in maze_lines])
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
    np.save("processed_map.npy", grid)

    return entry, ex, path_str


def terminal_display(entry: tuple, exit_coord: tuple, path_str: str) -> None:
    bit_map = np.load("processed_map.npy")

    vis_grid = [
        ["██" if cell == 1 else "  " for cell in row] for row in bit_map]
    start_r, start_c = 2 * entry[1] + 1, 2 * entry[0] + 1
    end_r, end_c = 2 * exit_coord[1] + 1, 2 * exit_coord[0] + 1

    cmd: str = 'cls' if os.name == 'nt' else 'clear'
    subprocess.run(cmd, shell=True)

    vis_grid[start_r][start_c] = "SS"
    vis_grid[end_r][end_c] = "EE"

    curr_r, curr_c = start_r, start_c
    for move in path_str:
        dr, dc = 0, 0
        if move == 'N':
            dr = -1
        elif move == 'S':
            dr = 1
        elif move == 'E':
            dc = 1
        elif move == 'W':
            dc = -1

        for _ in range(2):
            curr_r += dr
            curr_c += dc

            if vis_grid[curr_r][curr_c] == "  ":
                vis_grid[curr_r][curr_c] = "··"

        print("\033[H", end="")
        for row in vis_grid:
            print("".join(row))
        time.sleep(0.05)


def dt() -> None:
    terminal_display(bin_maze("utilities/output_maze.txt"))
