import numpy as np


class MazeModel:
    def __init__(self, filepath: str, start: tuple[int, int],
                 end: tuple[int, int]) -> None:
        self.grid = np.load(filepath)
        self.start = start
        self.end = end

        self.rows, self.cols = self.grid.shape

    def is_wall(self, row: int, col: int) -> bool:
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.grid[row, col] == 1
        return False

    def get_cell_size(self, window_width: int, window_height: int) -> float:
        cell_w = window_width / self.cols
        cell_h = window_height / self.rows
        return min(cell_w, cell_h)

    def get_grid_offset(self, window_width: int, window_height: int, cell_size: float) -> tuple[float, float]:
        maze_pixel_width = self.cols * cell_size
        maze_pixel_height = self.rows * cell_size

        offset_x = (window_width - maze_pixel_width) / 2
        offset_y = (window_height - maze_pixel_height) / 2
        return offset_x, offset_y
