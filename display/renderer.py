import numpy as np
from structure.MazeModel import MazeModel
from enum import Enum


class AnimationState(Enum):
    EXPLORING = 1
    DRAWING_PATH = 2
    FINISHED = 3


class MazeRenderer:
    def __init__(
        self,
        model: MazeModel,
        visited_steps: list[tuple[int, int]],
        final_path: list[tuple[int, int]],
    ) -> None:
        self.model = model
        self.visited_steps = visited_steps
        self.final_path = final_path

        self.state = AnimationState.EXPLORING
        self.step_index = 0
        self.path_index = 0

        self.COLOR_BG: int = 0xFF1E1E2E
        self.COLOR_WALL: int = 0xFF45475A
        self.COLOR_START: int = 0xFF89B4FA
        self.COLOR_END: int = 0xFFF38BA8
        self.COLOR_VISITED: int = 0xFF89DCEB
        self.COLOR_PATH: int = 0xFFA6E3A1

    def draw_cell(
        self,
        screen: np.ndarray,
        row: int,
        col: int,
        color: int,
        cell_size: float,
        offset_x: float,
        offset_y: float
    ) -> None:
        height, width = screen.shape
        x_start = int(offset_x + col * cell_size)
        y_start = int(offset_y + row * cell_size)
        size = int(cell_size)

        y_end = min(y_start + size, height)
        x_end = min(x_start + size, width)

        if x_start < x_end and y_start < y_end:
            screen[y_start:y_end, x_start:x_end] = color

    def render_frame(self, screen: np.ndarray) -> None:
        height, width = screen.shape

        screen[:, :] = self.COLOR_BG

        cell_size = self.model.get_cell_size(width, height)
        offset_x, offset_y = self.model.get_grid_offset(width, height,
                                                        cell_size)

        # Dibujar paredes
        for r in range(self.model.rows):
            for c in range(self.model.cols):
                if self.model.is_wall(r, c):
                    self.draw_cell(
                        screen, r, c, self.COLOR_WALL, cell_size, offset_x,
                        offset_y
                    )

        # Dibujar casillas visitadas
        for i in range(min(self.step_index, len(self.visited_steps))):
            r, c = self.visited_steps[i]
            self.draw_cell(
                screen, r, c, self.COLOR_VISITED, cell_size, offset_x, offset_y
            )

        # Dibujar el camino final
        if self.state in (AnimationState.DRAWING_PATH,
                          AnimationState.FINISHED):
            for i in range(min(self.path_index, len(self.final_path))):
                r, c = self.final_path[i]
                self.draw_cell(
                    screen, r, c, self.COLOR_PATH, cell_size, offset_x,
                    offset_y
                )

        # Dibujar Entrada y Salida
        sr, sc = self.model.start
        er, ec = self.model.end
        self.draw_cell(screen, sr, sc, self.COLOR_START, cell_size, offset_x,
                       offset_y)
        self.draw_cell(screen, er, ec, self.COLOR_END, cell_size, offset_x,
                       offset_y)

    def update_animation(self) -> None:
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
