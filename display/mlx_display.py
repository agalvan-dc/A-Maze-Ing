import ctypes
import math
import os
import random
from typing import Any, Optional

import numpy as np
from mlx import Mlx

from .renderer import AnimationState, MazeRenderer
from display.terminal_display import bin_maze
from engine.Player import Player
from engine.buffer import EngineRenderer
from structure import MazeModel, MazeSolver
from structure.parsing import validate_conf
from mazegen import MazeGenerator


def random_color() -> int:
    """Generate a random opaque RGB color.

    Returns:
        A 32-bit ARGB color.
    """
    r = random.randint(100, 255)
    g = random.randint(100, 255)
    b = random.randint(100, 255)

    return (0xFF << 24) | (r << 16) | (g << 8) | b


def create_generator(config: dict[str, Any]) -> MazeGenerator:
    """Create a MazeGenerator from the project configuration.

    Args:
        config: Validated maze configuration.

    Returns:
        A configured MazeGenerator instance.
    """
    seed = config["seed"]

    if seed in ("", "random", "RANDOM"):
        seed = None

    perfect = config["perfect"]

    if isinstance(perfect, str):
        perfect = perfect == "True"

    return MazeGenerator(
        width=int(config["width"]),
        height=int(config["height"]),
        seed=seed,
        entry=tuple(config["entry"]),
        exit=tuple(config["exit"]),
        perfect=perfect,
    )


class MazeController:
    """Coordinate maze generation, solving, rendering, and player state."""

    def __init__(
        self,
        renderer: MazeRenderer,
        generator: MazeGenerator,
        player: Optional[Player] = None,
        renderer_3d: Optional[EngineRenderer] = None,
    ) -> None:
        """Initialize the maze controller.

        Args:
            renderer: 2D maze renderer.
            generator: Maze generator.
            player: Optional 3D player.
            renderer_3d: Optional 3D renderer.
        """
        self.renderer = renderer
        self.generator = generator
        self.player = player
        self.renderer_3d = renderer_3d

    def gen(self) -> None:
        """Generate a maze and update all rendering components."""
        self.generator.generate()

        filepath = "utilities/maze_output.txt"

        logical_entry, logical_ex, path_str = bin_maze(filepath)

        if self.renderer.model is None:
            raise RuntimeError("Maze renderer requires a maze model.")

        model = self.renderer.model

        model.grid = np.load("utilities/processed_map.npy")
        model.rows = int(model.grid.shape[0])
        model.cols = int(model.grid.shape[1])

        physical_entry = (
            logical_entry[1] * 2 + 1,
            logical_entry[0] * 2 + 1,
        )

        physical_ex = (
            logical_ex[1] * 2 + 1,
            logical_ex[0] * 2 + 1,
        )

        model.start = physical_entry
        model.end = physical_ex

        new_solver = MazeSolver(
            model,
            logical_entry,
            logical_ex,
        )

        logical_visited = new_solver.get_visited()

        visited_set = set(logical_visited)
        physical_visited: set[tuple[int, int]] = set()

        for x, y in logical_visited:
            row = y * 2 + 1
            col = x * 2 + 1

            physical_visited.add((row, col))

            neighbors = (
                (x + 1, y),
                (x - 1, y),
                (x, y + 1),
                (x, y - 1),
            )

            for nx, ny in neighbors:
                if (nx, ny) not in visited_set:
                    continue

                if not new_solver.can_move(x, y, nx, ny):
                    continue

                next_row = ny * 2 + 1
                next_col = nx * 2 + 1

                physical_visited.add(
                    (
                        (row + next_row) // 2,
                        (col + next_col) // 2,
                    )
                )

                physical_visited.add(
                    (next_row, next_col)
                )

        self.renderer.visited_steps = list(physical_visited)

        physical_path: list[tuple[int, int]] = []

        current_row = logical_entry[1] * 2 + 1
        current_col = logical_entry[0] * 2 + 1

        physical_path.append(
            (current_row, current_col)
        )

        for move in path_str:
            if move == "N":
                delta_row, delta_col = -1, 0
            elif move == "S":
                delta_row, delta_col = 1, 0
            elif move == "E":
                delta_row, delta_col = 0, 1
            elif move == "W":
                delta_row, delta_col = 0, -1
            else:
                continue

            current_row += delta_row
            current_col += delta_col

            physical_path.append(
                (current_row, current_col)
            )

            current_row += delta_row
            current_col += delta_col

            physical_path.append(
                (current_row, current_col)
            )

        self.renderer.final_path = physical_path

        if self.renderer_3d:
            self.renderer_3d.update_path(
                physical_path,
                physical_ex,
            )

        self.renderer.step_index = 0
        self.renderer.path_index = 0
        self.renderer.state = AnimationState.EXPLORING

        self._reset_player(physical_path)

    def _reset_player(
        self,
        physical_path: list[tuple[int, int]],
    ) -> None:
        """Reset the 3D player to the beginning of the solution path.

        Args:
            physical_path: Physical coordinates of the solution.
        """
        if not self.player or len(physical_path) <= 1:
            return

        start_row, start_col = physical_path[0]

        self.player.pos_x = float(start_col) + 0.5
        self.player.pos_y = float(start_row) + 0.5

        next_row, next_col = physical_path[1]

        direction_x = float(next_col - start_col)
        direction_y = float(next_row - start_row)

        length = math.hypot(
            direction_x,
            direction_y,
        )

        if length == 0:
            return

        self.player.dir_x = direction_x / length
        self.player.dir_y = direction_y / length

        fov_multiplier = 0.66

        self.player.x_plane = (
            -self.player.dir_y * fov_multiplier
        )

        self.player.y_plane = (
            self.player.dir_x * fov_multiplier
        )

    def show(self) -> None:
        """Toggle visibility of the solution path."""
        if self.renderer.path_index > 0:
            self.renderer.path_index = 0
        else:
            self.renderer.path_index = len(
                self.renderer.final_path
            )

        self.renderer.state = AnimationState.FINISHED

    def animation(self) -> None:
        """Reset the maze animation and start exploration."""
        self.renderer.step_index = 0
        self.renderer.path_index = 0
        self.renderer.state = AnimationState.EXPLORING

    def rand_color(self) -> None:
        """Assign random colors to the 2D maze renderer."""
        self.renderer.COLOR_BG = random_color()
        self.renderer.COLOR_WALL = random_color()
        self.renderer.COLOR_PATH = random_color()
        self.renderer.COLOR_VISITED = random_color()


class mlx_buffer:
    """Manage the MLX window, buffers, events, and renderers."""

    def __init__(
        self,
        width: int = 800,
        height: int = 600,
        renderer_2d: Optional[MazeRenderer] = None,
        renderer_3d: Optional[EngineRenderer] = None,
        maze_ctrl: Optional[MazeController] = None,
        player: Optional[Player] = None,
    ) -> None:
        """Initialize the MLX window and rendering resources.

        Args:
            width: Display width.
            height: Display height.
            renderer_2d: Optional 2D renderer.
            renderer_3d: Optional 3D renderer.
            maze_ctrl: Optional maze controller.
            player: Optional 3D player.
        """
        self._width = width
        self._height = height
        self._ui_width = 300

        self.maze_ctrl = maze_ctrl
        self._renderer_2d = renderer_2d
        self._renderer_3d = renderer_3d
        self.player = player

        self.active_mode = "2D"
        self.keys_pressed: set[int] = set()

        self.m = Mlx()

        self._mlx_ptr = self.m.mlx_init()

        self._win_ptr = self.m.mlx_new_window(
            self._mlx_ptr,
            self._width + self._ui_width,
            self._height,
            "A-Maze-Ing",
        )

        self._img_ptr = self.m.mlx_new_image(
            self._mlx_ptr,
            self._width,
            self._height,
        )

        self._ui_bg_ptr = self.m.mlx_new_image(
            self._mlx_ptr,
            self._ui_width,
            self._height,
        )

        data_info = self.m.mlx_get_data_addr(
            self._img_ptr
        )

        pixel_array_type = ctypes.c_uint32 * (
            self._width * self._height
        )

        self.pixel_buffer = pixel_array_type.from_buffer(
            data_info[0]
        )

        self.screen = np.frombuffer(
            self.pixel_buffer,
            dtype=np.uint32,
        ).reshape(
            (self._height, self._width)
        )

        self.setup_hooks()
        self.draw_menu()

        if self._renderer_3d:
            wall = self.load_xpm_texture(
                "utilities/wall.xpm"
            )
            floor = self.load_xpm_texture(
                "utilities/floor.xpm"
            )
            path = self.load_xpm_texture(
                "utilities/path.xpm"
            )

            self._renderer_3d.set_textures(
                wall,
                floor,
                path,
            )

    @property
    def width(self) -> int:
        """Return the screen width."""
        return self._width

    @property
    def height(self) -> int:
        """Return the screen height."""
        return self._height

    @property
    def img_ptr(self) -> Any:
        """Return the MLX image pointer."""
        return self._img_ptr

    def setup_hooks(self) -> None:
        """Register MLX keyboard and window hooks."""
        self.m.mlx_hook(
            self._win_ptr,
            2,
            1 << 0,
            self.key_press,
            None,
        )

        self.m.mlx_hook(
            self._win_ptr,
            3,
            1 << 1,
            self.key_release,
            None,
        )

        self.m.mlx_hook(
            self._win_ptr,
            17,
            0,
            self.close,
            None,
        )

    def key_press(
        self,
        keycode: int,
        param: Optional[Any] = None,
    ) -> None:
        """Handle a keyboard key press."""
        if keycode in (65307, 53):
            self.close()
            return

        if keycode in (109, 65289, 46, 48):
            self.active_mode = (
                "3D"
                if self.active_mode == "2D"
                else "2D"
            )
            self.draw_menu()
            return

        if self.maze_ctrl:
            if keycode in (117, 32, 85):
                self.maze_ctrl.gen()

            elif keycode in (105, 34, 73):
                self.maze_ctrl.show()

            elif keycode in (111, 31, 79):
                self.maze_ctrl.animation()

            elif keycode in (112, 35, 80):
                self.maze_ctrl.rand_color()

        self.keys_pressed.add(keycode)

    def key_release(
        self,
        keycode: int,
        param: Optional[Any] = None,
    ) -> None:
        """Handle a keyboard key release."""
        self.keys_pressed.discard(keycode)

    def process_movement(self) -> None:
        """Process player movement and camera rotation."""
        if not self.player or self.active_mode != "3D":
            return

        move_speed = 0.05
        rotation_speed = 0.04

        if 119 in self.keys_pressed:
            self.player.move_forward(move_speed)

        if 115 in self.keys_pressed:
            self.player.move_backward(move_speed)

        if 97 in self.keys_pressed:
            self.player.move_left(move_speed)

        if 100 in self.keys_pressed:
            self.player.move_right(move_speed)

        if (
            65361 in self.keys_pressed
            or 123 in self.keys_pressed
        ):
            self.player.rotate(-rotation_speed)

        if (
            65363 in self.keys_pressed
            or 124 in self.keys_pressed
        ):
            self.player.rotate(rotation_speed)

    def load_xpm_texture(
        self,
        filepath: str,
    ) -> np.ndarray:
        """Load an XPM texture into a NumPy array.

        Args:
            filepath: XPM texture path.

        Returns:
            Texture represented as uint32 pixels.
        """
        img_ptr, width, height = (
            self.m.mlx_xpm_file_to_image(
                self._mlx_ptr,
                filepath,
            )
        )

        if not img_ptr:
            fallback = np.full(
                (64, 64),
                0xFFFF00FF,
                dtype=np.uint32,
            )

            fallback[::2, ::2] = 0xFF000000
            fallback[1::2, 1::2] = 0xFF000000

            return fallback

        data_info = self.m.mlx_get_data_addr(
            img_ptr
        )

        pixel_array_type = ctypes.c_uint32 * (
            width * height
        )

        pixel_buffer = pixel_array_type.from_buffer(
            data_info[0]
        )

        texture = np.frombuffer(
            pixel_buffer,
            dtype=np.uint32,
        ).reshape(
            (height, width)
        ).copy()

        self.m.mlx_destroy_image(
            self._mlx_ptr,
            img_ptr,
        )

        return texture

    def draw_menu(self) -> None:
        """Render the side-panel controls."""
        colour = 0x00FFFFFF

        base_x = self._width + 20
        base_y = 50

        self.m.mlx_put_image_to_window(
            self._mlx_ptr,
            self._win_ptr,
            self._ui_bg_ptr,
            self._width,
            0,
        )

        self.m.mlx_string_put(
            self._mlx_ptr,
            self._win_ptr,
            base_x,
            base_y,
            colour,
            f"Actual Mode: {self.active_mode}",
        )

        self.m.mlx_string_put(
            self._mlx_ptr,
            self._win_ptr,
            base_x,
            base_y + 30,
            colour,
            "-------------------------",
        )

        if self.active_mode == "2D":
            controls = (
                "[M/TAB] Change mode",
                "[U] Regen maze",
                "[I] Show / Hide Path",
                "[O] Animate",
                "[P] Change theme",
            )
        else:
            controls = (
                "[W/A/S/D] Move",
                "[< / >]   Rotate cam",
            )

        for index, text in enumerate(controls):
            self.m.mlx_string_put(
                self._mlx_ptr,
                self._win_ptr,
                base_x,
                base_y + 60 + index * 30,
                colour,
                text,
            )

    def render_frame(
        self,
        param: Optional[Any] = None,
    ) -> int:
        """Render one frame of the application.

        Args:
            param: MLX callback parameter.

        Returns:
            Zero to continue the event loop.
        """
        self.process_movement()

        if (
            self.active_mode == "2D"
            and self._renderer_2d
        ):
            self._renderer_2d.update_animation()
            self._renderer_2d.render_frame(
                self.screen
            )

        elif (
            self.active_mode == "3D"
            and self._renderer_3d
        ):
            self._renderer_3d.render_frame(
                self.screen
            )

        self.m.mlx_put_image_to_window(
            self._mlx_ptr,
            self._win_ptr,
            self._img_ptr,
            0,
            0,
        )

        self.m.mlx_do_sync(self._mlx_ptr)

        return 0

    def close(
        self,
        param: Optional[Any] = None,
    ) -> None:
        """Release MLX resources and terminate the application."""
        if self._ui_bg_ptr:
            self.m.mlx_destroy_image(
                self._mlx_ptr,
                self._ui_bg_ptr,
            )

        if self._img_ptr:
            self.m.mlx_destroy_image(
                self._mlx_ptr,
                self._img_ptr,
            )

        if self._win_ptr:
            self.m.mlx_destroy_window(
                self._mlx_ptr,
                self._win_ptr,
            )

        self.m.mlx_release(self._mlx_ptr)

        os._exit(0)

    def run(self) -> None:
        """Start the MLX event loop."""
        self.m.mlx_loop_hook(
            self._mlx_ptr,
            self.render_frame,
            None,
        )

        self.m.mlx_loop(self._mlx_ptr)


def mlx_display(
    entry: tuple[int, int],
    ex: tuple[int, int],
    path_str: str,
) -> None:
    """Initialize and start the MLX maze display.

    Args:
        entry: Logical maze entry coordinates.
        ex: Logical maze exit coordinates.
        path_str: Logical solution path.
    """
    physical_entry = (
        entry[1] * 2 + 1,
        entry[0] * 2 + 1,
    )

    physical_exit = (
        ex[1] * 2 + 1,
        ex[0] * 2 + 1,
    )

    maze_model = MazeModel(
        "utilities/processed_map.npy",
        physical_entry,
        physical_exit,
    )

    player = Player(maze_model)

    config = validate_conf(
        "utilities/config.txt"
    )

    generator = create_generator(config)

    renderer_2d = MazeRenderer(
        model=maze_model,
        visited_steps=[],
        final_path=[],
    )

    renderer_3d = EngineRenderer(
        model=maze_model,
        player=player,
        width=1200,
        height=800,
    )

    controller = MazeController(
        renderer=renderer_2d,
        generator=generator,
        player=player,
        renderer_3d=renderer_3d,
    )

    window = mlx_buffer(
        width=1200,
        height=800,
        renderer_2d=renderer_2d,
        renderer_3d=renderer_3d,
        maze_ctrl=controller,
        player=player,
    )

    if window.maze_ctrl is None:
        raise RuntimeError(
            "Maze controller was not initialized."
        )

    window.maze_ctrl.gen()
    window.maze_ctrl.animation()
    window.run()
