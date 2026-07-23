import numpy as np
from mlx import Mlx
from collections.abc import Callable
from typing import Optional
from .terminal_display import bin_maze
from ..structure.MazeModel impoert MazeModel

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
        cell_w = window_width / self.rows
        cell_h = window_height / self.cols
        return min(cell_w, cell_h)

    def get_grid_offset(self, window_width: int, window_height: int, cell_size: float) -> tuple[float, float]:
        maze_pixel_width = self.cols * cell_size
        maze_pixel_height = self.rows * cell_size

        offset_x = (window_width - maze_pixel_width) / 2
        offset_y = (window_height - maze_pixel_height) / 2
        return offset_x, offset_y


class ResponsiveBuffer:
    def __init__(self,
                 initial_width: int = 800,
                 initial_height: int = 600,
                 render: Optional[Callable[['ResponsiveBuffer'], None]] = None
                 ) -> None:
        self.m = Mlx()
        self.mlx_ptr = self.m.mlx_init()
        self.width = initial_width
        self.height = initial_height
        self.render_callback = render

        self.win_ptr = self.m.mlx_new_window(
            self.mlx_ptr, self.width, self.height, "Maze Solver MLX"
        )

        self.img_ptr = None
        self.update_buffer(self.width, self.height)

        self.m.mlx_hook(self.win_ptr, 22, 0, self.on_resize, None)
        self.m.mlx_expose_hook(self.win_ptr, self.on_resize, None)

        self.m.mlx_key_hook(self.win_ptr, self.on_key_press, None)
        self.m.mlx_hook(self.win_ptr, 17, 0, self.close, None)

    def update_buffer(self, new_width, new_height) -> None:
        if self.img_ptr:
            self.m.mlx_destroy_image(self.mlx_ptr, self.img_ptr)

        self.width = new_width
        self.height = new_height
        self.img_ptr = self.m.mlx_new_image(self.mlx_ptr,
                                            self.width, self.height)

    def render_frame(self) -> None:
        if self.render_callback:
            self.render_callback(self)

        self.m.mlx_put_image_to_window(
            self.mlx_ptr, self.win_ptr, self.img_ptr, 0, 0
        )

    def on_resize(self, param) -> None:
        self.update_buffer(self.width, self.height)
        self.render_frame()

    def on_key_press(self, keycode, param):
        if keycode == 65307:
            self.close(param)

    def close(self, param=None) -> None:
        if self.img_ptr:
            self.m.mlx_destroy_image(self.mlx_ptr, self.img_ptr)
        self.m.mlx_destroy_window(self.mlx_ptr, self.win_ptr)
        self.m.mlx_loop_exit(self.mlx_ptr)


    def run(self, update_loop_callback=None):
        if update_loop_callback:
            self.m.mlx_loop_hook(self.mlx_ptr, update_loop_callback, None)

        self.render_frame()
        self.m.mlx_loop(self.mlx_ptr)
        self.m.mlx_release(self.mlx_ptr)


def mlx_2d_display(entry: tuple, exit: tuple, path_str: str) -> None:

    mlx_window = ResponsiveBuffer(800, 600)
    maze = MazeModel("processed_map.npy", entry, exit)

    Mlx.mlx_release()
