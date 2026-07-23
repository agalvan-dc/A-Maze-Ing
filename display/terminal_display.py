import numpy as np
import os
import time
import subprocess


def bin_maze(data: dict, filepath: str) -> None:

    with open(filepath, 'r', encoding='utf-8') as file:
        map_bits = np.array(
            [[int(char, 16) for char in line.strip()] for line in file])
    h, w = map_bits.shape

    grid = np.zeros(
        (2 * h + 1, 2 * w + 1), '  ', dtype=np.uint8)
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


def terminal_display() -> None:
    bit_map = np.load("processed_map.npy")
    cmd: str = 'cls' if os.name == 'nt' else 'clear'
    subprocess.run(cmd, shell=True)

    for row in bit_map:
        line = "".join("██" if cell == 1 else "  " for cell in row)
        print(line)
        time.sleep(0.05)
