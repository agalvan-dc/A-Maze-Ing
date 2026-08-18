import numpy as np
from typing import Any


class MazeModel:
    """Represent the physical maze grid and its display geometry."""

    def __init__(
        self,
        filepath: str,
        start: tuple[int, int],
        end: tuple[int, int]
    ) -> None:
        """Initialize the maze model from a NumPy grid file.

        Args:
            filepath: Path to the NumPy file containing the maze grid.
            start: Starting position as a (column, row) coordinate.
            end: Ending position as a (column, row) coordinate.
        """
        self.grid: np.ndarray[Any, np.dtype[np.int_]] = np.load(filepath)

        self.start = start
        self.end = end

        self.rows: int = int(self.grid.shape[0])
        self.cols: int = int(self.grid.shape[1])

    def is_wall(self, x: int, y: int) -> bool:
        """Check whether a physical grid position is blocked.

        Coordinates use x for the column and y for the row. Grid values
        represent 0 as traversable space, 1 as a wall, and 2 as the 42 cell.
        Positions outside the grid are considered blocked.

        Args:
            x: Column index of the grid position.
            y: Row index of the grid position.

        Returns:
            True if the position is outside the grid or contains a
            non-traversable cell, otherwise False.
        """
        if not (
            0 <= x < self.cols
            and 0 <= y < self.rows
        ):
            return True

        return bool(self.grid[y, x] != 0)

    def get_cell_size(
        self,
        window_width: int,
        window_height: int
    ) -> float:
        """Calculate the display size of a single maze cell.

        The returned size preserves the maze proportions and ensures that
        the complete grid fits inside the given window.

        Args:
            window_width: Width of the rendering window in pixels.
            window_height: Height of the rendering window in pixels.

        Returns:
            The cell size in pixels.
        """
        cell_w: float = window_width / self.cols
        cell_h: float = window_height / self.rows

        return float(min(cell_w, cell_h))

    def get_grid_offset(
        self,
        window_width: int,
        window_height: int,
        cell_size: float
    ) -> tuple[float, float]:
        """Calculate the offset required to center the maze in the window.

        Args:
            window_width: Width of the rendering window in pixels.
            window_height: Height of the rendering window in pixels.
            cell_size: Display size of each maze cell in pixels.

        Returns:
            A tuple containing the horizontal and vertical offsets in pixels.
        """
        maze_pixel_width: float = self.cols * cell_size
        maze_pixel_height: float = self.rows * cell_size

        offset_x: float = (
            window_width - maze_pixel_width
        ) / 2

        offset_y: float = (
            window_height - maze_pixel_height
        ) / 2

        return offset_x, offset_y
