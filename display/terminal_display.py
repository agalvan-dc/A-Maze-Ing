import sys
import time
from typing import Optional
import numpy as np
from .read_data import read_maze_data as read_m


def bin_maze(filepath: str) -> tuple:

    maze_lines, entry, ex, path_str = read_m(filepath)

    map_bits = np.array(
        [
            [-1 if char.upper() == "F" else int(char, 16)
             for char in line]
            for line in maze_lines
        ]
    )

    h, w = map_bits.shape

    grid = np.zeros(
        (2 * h + 1, 2 * w + 1),
        dtype=np.uint8
    )

    grid[0::2, 0::2] = 1

    for r in range(h):
        for c in range(w):
            val = map_bits[r, c]

            cr = 2 * r + 1
            cc = 2 * c + 1

            if val == -1:
                grid[cr, cc] = 2

                if r > 0 and map_bits[r - 1, c] == -1:
                    grid[cr - 1, cc] = 2

                if r < h - 1 and map_bits[r + 1, c] == -1:
                    grid[cr + 1, cc] = 2

                if c > 0 and map_bits[r, c - 1] == -1:
                    grid[cr, cc - 1] = 2

                if c < w - 1 and map_bits[r, c + 1] == -1:
                    grid[cr, cc + 1] = 2

                continue

            if val & 1:
                grid[cr - 1, cc] = 1

            if val & 2:
                grid[cr, cc + 1] = 1

            if val & 4:
                grid[cr + 1, cc] = 1

            if val & 8:
                grid[cr, cc - 1] = 1

    np.save("utilities/processed_map.npy", grid)

    return (
        (int(entry[0]), int(entry[1])),
        (int(ex[0]), int(ex[1])),
        path_str
    )


def terminal_display(entry: tuple[int, int],
                     exit_coord: tuple[int, int],
                     path_str: str,
                     path_color: Optional[int] = None,
                     wall_color: Optional[int] = None) -> None:

    c_start = "\033[92m"
    c_end = "\033[91m"
    c_reset = "\033[0m"
    c_42 = "\033[38;5;208m"

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

    vis_grid = []

    for row in bit_map:
        new_row = []

        for cell in row:
            if cell == 1:
                new_row.append(f"{c_wall}██{c_reset}")
            elif cell == 2:
                new_row.append(f"{c_42}██{c_reset}")
            else:
                new_row.append("  ")

        vis_grid.append(new_row)

    # Coordenadas LOGICAS -> coordenadas FISICAS
    start_r = entry[1] * 2 + 1
    start_c = entry[0] * 2 + 1

    end_r = exit_coord[1] * 2 + 1
    end_c = exit_coord[0] * 2 + 1

    vis_grid[start_r][start_c] = f"{c_start}██{c_reset}"
    vis_grid[end_r][end_c] = f"{c_end}██{c_reset}"

    curr_r = start_r
    curr_c = start_c

    moves = {
        'N': (-1, 0),
        'S': (1, 0),
        'E': (0, 1),
        'W': (0, -1)
    }

    sys.stdout.write("\033[H\033[J")

    output = "\n".join(
        "".join(row)
        for row in vis_grid
    )

    sys.stdout.write(output + "\n")
    sys.stdout.flush()

    time.sleep(0.5)

    # Cada dirección del output representa
    # un movimiento entre DOS celdas físicas.
    for move in path_str:

        dr, dc = moves[move]

        for _ in range(2):

            curr_r += dr
            curr_c += dc

            if (
                0 <= curr_r < len(vis_grid)
                and 0 <= curr_c < len(vis_grid[0])
            ):
                if vis_grid[curr_r][curr_c] == "  ":
                    vis_grid[curr_r][curr_c] = (
                        f"{c_path}██{c_reset}"
                    )

            sys.stdout.write("\033[H\033[J")

            output = "\n".join(
                "".join(row)
                for row in vis_grid
            )

            sys.stdout.write(output + "\n")
            sys.stdout.flush()

            time.sleep(0.05)


def dt(path_color=None, wall_color=None):
    entry, ex, path = bin_maze("utilities/maze_output.txt")
    terminal_display(
        entry,
        ex,
        path,
        path_color,
        wall_color
    )
