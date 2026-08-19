from enum import Enum
from typing import Union
from structure import MazeModel
import numpy as np


class AnimationState(Enum):
    """Enum class for animation output"""

    EXPLORING = 1
    DRAWING_PATH = 2
    FINISHED = 3


class MazeRenderer:
    """Class in charge of rendering 2d output. It manages both
        maze drawing and maze animation

        Attributes:
            model -> data model that contains maze structure
            visited_steps -> coordinates visited during maze exit search
            final_path -> final maze solution
            state(AnimationState) -> actual animation state
            step_index -> actual index in the visited steps list
            path_index -> actual index in the final path list
            steps_per_frame -> number of steps processed per animation frame
            COLOR_BG -> background color
            COLOR_WALL -> wall color
            COLOR_START -> start color
            COLOR_END -> end color
            COLOR_VISITED -> visited color
            COLOR_PATH -> path color
    """

    def __init__(
        self,
        model: MazeModel,
        visited_steps: list[tuple[int, int]],
        final_path: Union[str, list[tuple[int, int]]],
    ) -> None:

        """Initializes render components, maze state and maze color

            Args:
                model: maze that is about to be rendered (can be none)
                visited_steps: organized search sequence of visited maze steps
                final_path: maze solution as a str or a coor list
        """
        self.model = model
        self.visited_steps = visited_steps

        """Initializes render components, maze state and maze color."""

        self.model = model

        if isinstance(final_path, str):
            if self.model is None:
                raise RuntimeError(
                    "MazeRenderer requires a maze model "
                    "when final_path is a string."
                )

            self.final_path = self._path_str_to_coords(
                self.model.start,
                final_path
            )
        else:
            self.final_path = final_path

        self.visited_steps = visited_steps

        self.state = AnimationState.EXPLORING
        self.step_index = 0
        self.path_index = 0

        self.steps_per_frame = 1

        self.COLOR_BG: int = 0xFF1E1E2E
        self.COLOR_WALL: int = 0xFF45475A
        self.COLOR_START: int = 0xFF89B4FA
        self.COLOR_END: int = 0xFFF38BA8
        self.COLOR_VISITED: int = 0xFF89DCEB
        self.COLOR_PATH: int = 0xFFA6E3A1
        self.COLOR_42: int = 0xFFFF8800

    def _path_str_to_coords(
        self, start: tuple[int, int], path_str: str
    ) -> list[tuple[int, int]]:
        """Converts a directional text path str into
        a sequence of maze coordinates.

        Each directional character (N, S, E, W) shifts the position by 2 units
        to account for structural walls between maze rooms

        Args:
            start: the initial coor tuple (row, col) to begin tracking from
            path_str: a str of chars representing cardinal directions

        Return:
            a list of coordinates that lead to the end maze point, tracking
            every step till the end
        """
        moves = {'N': (-1, 0), 'S': (1, 0), 'E': (0, 1), 'W': (0, -1)}
        curr_r, curr_c = start
        coords = [(curr_r, curr_c)]

        for move in path_str:
            dr, dc = moves.get(move, (0, 0))
            for _ in range(2):
                curr_r += dr
                curr_c += dc
                coords.append((curr_r, curr_c))

        return coords

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
        """Renders a single square grid cell on the target pixel buffer screen

           Calculates the exact matrix pixel boundaries for the cell and
           overwrites the slice with the specified color value while preventing
           screen overflow

           Args:
                screen: a 2 dimension NumPy array
                    representing pixel display buffer
                row: the row index of the target cell in the maze grid layout
                col: the col index of the target cell in the maze grid layout
                color: the hexadecimal color value applied to the cell pixels
                cell_size: the visual width and height
                    of a single cell in pixels
                offset_x: horizontal shift padding to
                    center-align the grid on the screen
                offset_y: vertical shift padding to
                    center-align the grid on the screen
        """
        height, width = screen.shape
        x_start = int(offset_x + col * cell_size)
        y_start = int(offset_y + row * cell_size)
        size = int(cell_size)

        y_end = min(y_start + size, height)
        x_end = min(x_start + size, width)

        if x_start < x_end and y_start < y_end:
            screen[y_start:y_end, x_start:x_end] = color

    def render_frame(self, screen: np.ndarray) -> None:
        """Draws the current frame of the maze animation
           state onto the screen buffer

           Clears the screen withh the background color, renders static walls,
           and then layers active elements like visited cells, solution path
           and endpoint based on the current animation progress

            Args:
                screen: a 2 dimension NumPy serving
                    as the target outputframe buffer
        """
        height, width = screen.shape

        screen[:, :] = self.COLOR_BG

        cell_size = self.model.get_cell_size(width, height)
        offset_x, offset_y = self.model.get_grid_offset(
            width, height, cell_size
        )

        for r in range(self.model.rows):
            for c in range(self.model.cols):

                cell = self.model.grid[r, c]

                if cell == 2:
                    self.draw_cell(
                        screen,
                        r,
                        c,
                        self.COLOR_42,
                        cell_size,
                        offset_x,
                        offset_y
                    )

                elif cell == 1:
                    self.draw_cell(
                        screen,
                        r,
                        c,
                        self.COLOR_WALL,
                        cell_size,
                        offset_x,
                        offset_y
                    )

        max_visited = min(
            self.step_index,
            len(self.visited_steps)
        )

        for i in range(max_visited):
            r, c = self.visited_steps[i]

            if self.model.grid[r, c] == 2:
                continue

            self.draw_cell(
                screen,
                r,
                c,
                self.COLOR_VISITED,
                cell_size,
                offset_x,
                offset_y
            )

        if self.state in (
            AnimationState.DRAWING_PATH,
            AnimationState.FINISHED
        ):
            max_path = min(
                self.path_index,
                len(self.final_path)
            )

            for i in range(max_path):
                r, c = self.final_path[i]

                if self.model.grid[r, c] == 2:
                    continue

                self.draw_cell(
                    screen,
                    r,
                    c,
                    self.COLOR_PATH,
                    cell_size,
                    offset_x,
                    offset_y
                )

        sr, sc = self.model.start
        er, ec = self.model.end

        self.draw_cell(
            screen,
            sr,
            sc,
            self.COLOR_START,
            cell_size,
            offset_x,
            offset_y
        )

        self.draw_cell(
            screen,
            er,
            ec,
            self.COLOR_END,
            cell_size,
            offset_x,
            offset_y
        )

    def update_animation(self) -> None:
        """Takes care of the animation. Advances indexes to step forward
           through the active visualization timeline

           Increments indexes by the frame config. Transitions the main
           animation state machine from exploring to drawing the final path
           and finally stops updating once the destination path is completed.
        """
        if self.state == AnimationState.FINISHED:
            return

        if self.state == AnimationState.EXPLORING:
            if self.step_index < len(self.visited_steps):
                self.step_index += self.steps_per_frame
            else:
                self.state = AnimationState.DRAWING_PATH

        elif self.state == AnimationState.DRAWING_PATH:
            if self.path_index < len(self.final_path):
                self.path_index += self.steps_per_frame
            else:
                self.state = AnimationState.FINISHED
