import numpy as np
from pathlib import Path


def generate_maze(input: dict) -> str:

    seed: int = np.random.seed(input['SEED']) if input['SEED'] else np.random
    arrival = Path("utilities")

    true_path = arrival/"output_maze.txt"
    with open(true_path, 'w', encoding='utf-8') as file:
        file.write()

