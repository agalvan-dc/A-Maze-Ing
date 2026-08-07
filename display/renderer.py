from mlx import Mlx
from ..structure.MazeModel import MazeModel, MazeSolver
from enum import Enum
from typing import Optional, TYPE_CHECKING
import ctypes

if TYPE_CHECKING:
    from .mlx_display import mlx_buffer

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

        self.COLOR_BG: int = 0x1E1E2E
        self.COLOR_WALL: int = 0x45475A
        self.COLOR_START: int = 0x89B4FA
        self.COLOR_END: int = 0xF38BA8
        self.COLOR_VISITED: int = 0x89DCEB
        self.COLOR_PATH: int = 0xA6E3A1

    def draw_cell(
        self,
        pixels,
        stride: int,
        buffer_width: int,
        buffer_height: int,
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


        y_end = min(y_start + size, buffer_height)
        x_end = min(x_start + size, buffer_width)

        for y in range(max(0, y_start), y_end):
            row_offset = y * stride
            for x in range(max(0, x_start), x_end):
                pixels[row_offset + x] = color

    def render_frame(self, buffer: "mlx_buffer") -> None:
        data_ptr, bpp, size_line, endian = buffer.m.mlx_get_data_addr(buffer.img_ptr)
        pixels = data_ptr.cast('I')
        stride = size_line // 4

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
                    pixels, stride, buffer.width, buffer.height,
                    r, c, color, cell_size, offset_x, offset_y
                )

        for i in range(min(self.step_index, len(self.visited_steps))):
            r, c = self.visited_steps[i]
            self.draw_cell(pixels, 
                           stride, buffer.width, buffer.height,
                           r, c, self.COLOR_VISITED,
                           cell_size, offset_x, offset_y
            )

        if self.state in (AnimationState.DRAWING_PATH, AnimationState.FINISHED):
            for i in range(min(self.path_index, len(self.final_path))):
                r, c = self.final_path[i]
                self.draw_cell(
                    pixels, stride, buffer.width, buffer.height,
                    r, c, self.COLOR_PATH, cell_size, offset_x, offset_y
                )

        sr, sc = self.model.start
        er, ec = self.model.end
        self.draw_cell(
            pixels, stride, buffer.width, buffer.height,
            sr, sc, self.COLOR_START, cell_size, offset_x, offset_y
        )
        self.draw_cell(
            pixels, stride, buffer.width, buffer.height,
            er, ec, self.COLOR_END, cell_size, offset_x, offset_y
        )

    def update_animation(
        self, buffer: "mlx_buffer", param: Optional[object] = None
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

