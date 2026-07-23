from mlx import Mlx
from collections.abc import Callable
from typing import Optional
from .terminal_display import bin_maze
from ..structure.MazeModel import MazeModel, MazeSolver
from enum import Enum
import ctypes


class AnimationState(Enum):
    EXPLORING = 1
    DRAWING_PATH = 2
    FINISHED = 3


class MazeRenderer:
    def __init__(
        self,
        model: MazeModel,
        visited_steps: list[tuple[int, int]],
        final_path: list[tuple[int, int]]
    ) -> None:
        self.model = model
        self.visited_steps = visited_steps
        self.final_path = final_path

        self.state = AnimationState.EXPLORING
        self.step_index = 0
        self.path_index = 0

        self.COLOR_BG = 0x1E1E2E
        self.COLOR_WALL = 0x45475A
        self.COLOR_START = 0x89B4FA
        self.COLOR_END = 0xF38BA8
        self.COLOR_VISITED = 0x89DCEB
        self.COLOR_PATH = 0xA6E3A1

    def draw_cell(
        self,
        buffer: ResponsiveBuffer,
        row: int,
        col: int,
        color: int,
        cell_size: float,
        offset_x: float,
        offset_y: float
    ) -> None:
        x_start = int(offset_x + col * cell_size)
        y_start = int(offset_y + row * cell_size)
        size = int(cell_size)

        data_ptr, bpp, size_line, endian = buffer.m.mlx_get_data_addr(
            buffer.img_ptr
        )

        pixels = ctypes.cast(
            data_ptr,
            ctypes.POINTER(ctypes.c_uint32)
        )

        stride = size_line // 4

        y_end = min(y_start + size, buffer.height)
        x_end = min(x_start + size, buffer.width)

        for y in range(max(0, y_start), y_end):
            row_offset = y * stride
            for x in range(max(0, x_start), x_end):
                pixels[row_offset + x] = color

    def render_frame(self, buffer: ResponsiveBuffer) -> None:
        cell_size = self.model.get_cell_size(
            buffer.width, buffer.height
        )
        offset_x, offset_y = self.model.get_grid_offset(
            buffer.width, buffer.height, cell_size
        )

        for r in range(self.model.rows):
            for c in range(self.model.cols):
                color = (
                    self.COLOR_WALL
                    if self.model.is_wall(r, c)
                    else self.COLOR_BG
                )
                self.draw_cell(
                    buffer, r, c, color, cell_size, offset_x, offset_y
                )

        for i in range(min(self.step_index, len(self.visited_steps))):
            r, c = self.visited_steps[i]
            self.draw_cell(
                buffer, r, c, self.COLOR_VISITED, cell_size, offset_x, offset_y
            )

        if self.state in (AnimationState.DRAWING_PATH, AnimationState.FINISHED):
            for i in range(min(self.path_index, len(self.final_path))):
                r, c = self.final_path[i]
                self.draw_cell(
                    buffer,
                    r, c, self.COLOR_PATH, cell_size, offset_x, offset_y
                )

        sr, sc = self.model.start
        er, ec = self.model.end
        self.draw_cell(
            buffer, sr, sc, self.COLOR_START, cell_size, offset_x, offset_y
        )
        self.draw_cell(
            buffer, er, ec, self.COLOR_END, cell_size, offset_x, offset_y
        )

    def update_animation(
        self, buffer: ResponsiveBuffer, param: Optional[object] = None
    ) -> None:
        if self.state == AnimationState.FINISHED:
            return

        if self.state == AnimationState.EXPLORING:
            if self.step_index < len(self.visited_steps):
                self.step_index += 1
            else:
                self.state = AnimationState.DRAWING_PATH

        elif self.state == AnimationState.DRAWING_PATH:
            if self.path_index < len(self.final_path):
                self.path_index += 1
            else:
                self.state = AnimationState.FINISHED

        buffer.render_frame()


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
