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
from structure import MazeGenerator, MazeModel, MazeSolver


def random_color() -> int:
    """Generate a random opaque RGB color.

    Returns:
        A random color represented as a 32-bit ARGB integer.
    """
    r = random.randint(100, 255)
    g = random.randint(100, 255)
    b = random.randint(100, 255)
    return (0xFF << 24) | (r << 16) | (g << 8) | b


class MazeController:
    """Coordinate maze generation, solving, rendering, and player state."""

    def __init__(
        self,
        renderer: MazeRenderer,
        generator: MazeGenerator,
        player: Optional[Player] = None,
        renderer_3d: Optional[EngineRenderer] = None
    ) -> None:
        """Initialize the maze controller.

        Args:
            renderer: Renderer responsible for the 2D maze display.
            generator: Maze generator used to create new mazes.
            player: Optional player used by the 3D renderer.
            renderer_3d: Optional renderer responsible for the 3D display.
        """
        self.renderer = renderer
        self.generator = generator
        self.player = player
        self.renderer_3d = renderer_3d

    def gen(self) -> None:
        """Generate a maze and update all rendering components."""
        config_data = self.generator.get_config()
        self.generator.generate_maze(config_data, "basic")

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
            logical_entry[0] * 2 + 1
        )

        physical_ex = (
            logical_ex[1] * 2 + 1,
            logical_ex[0] * 2 + 1
        )

        model.start = physical_entry
        model.end = physical_ex

        new_solver = MazeSolver(
            model,
            logical_entry,
            logical_ex
        )

        logical_visited = new_solver.get_visited()

        visited_set = set(logical_visited)
        physical_visited: set[tuple[int, int]] = set()

        for x, y in logical_visited:
            r = y * 2 + 1
            c = x * 2 + 1

            physical_visited.add((r, c))

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

                nr = ny * 2 + 1
                nc = nx * 2 + 1

                physical_visited.add((
                    (r + nr) // 2,
                    (c + nc) // 2
                ))

                physical_visited.add((nr, nc))

        self.renderer.visited_steps = list(physical_visited)

        physical_path: list[tuple[int, int]] = []

        current_r = logical_entry[1] * 2 + 1
        current_c = logical_entry[0] * 2 + 1

        physical_path.append((current_r, current_c))

        for move in path_str:
            if move == "N":
                dr, dc = -1, 0
            elif move == "S":
                dr, dc = 1, 0
            elif move == "E":
                dr, dc = 0, 1
            elif move == "W":
                dr, dc = 0, -1
            else:
                continue

            current_r += dr
            current_c += dc
            physical_path.append((current_r, current_c))

            current_r += dr
            current_c += dc
            physical_path.append((current_r, current_c))

        self.renderer.final_path = physical_path

        if self.renderer_3d:
            self.renderer_3d.update_path(
                physical_path,
                physical_ex
            )

        self.renderer.step_index = 0
        self.renderer.path_index = 0
        self.renderer.state = AnimationState.EXPLORING

        if self.player and len(physical_path) > 1:
            start_r, start_c = physical_path[0]

            self.player.pos_x = float(start_c) + 0.5
            self.player.pos_y = float(start_r) + 0.5

            next_r, next_c = physical_path[1]

            dir_x = float(next_c - start_c)
            dir_y = float(next_r - start_r)

            length = math.hypot(dir_x, dir_y)

            if length != 0:
                self.player.dir_x = dir_x / length
                self.player.dir_y = dir_y / length

                fov_multiplier = 0.66

                self.player.x_plane = (
                    -self.player.dir_y * fov_multiplier
                )

                self.player.y_plane = (
                    self.player.dir_x * fov_multiplier
                )

    def show(self) -> None:
        """Display the complete solution path immediately."""
        self.renderer.state = AnimationState.FINISHED
        self.renderer.path_index = len(self.renderer.final_path)

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
    """Manage the MLX window, input events, and rendering loop."""

    def __init__(
        self,
        width: int = 800,
        height: int = 600,
        renderer_2d: Optional[MazeRenderer] = None,
        renderer_3d: Optional[EngineRenderer] = None,
        maze_ctrl: Optional[MazeController] = None,
        player: Optional[Player] = None
    ) -> None:
        """Initialize the MLX window and rendering resources.

        Args:
            width: Window width in pixels.
            height: Window height in pixels.
            renderer_2d: Optional 2D maze renderer.
            renderer_3d: Optional 3D maze renderer.
            maze_ctrl: Optional maze controller.
            player: Optional player controlled in 3D mode.
        """
        self._width = width
        self._height = height
        self._img_ptr: Any = None

        self.maze_ctrl = maze_ctrl
        self._renderer_2d = renderer_2d
        self._renderer_3d = renderer_3d
        self.player = player

        self.active_mode = "2D"
        self._ignore_next_mouse: bool = False
        self.keys_pressed: set[int] = set()

        self.m = Mlx()
        self._mlx_ptr: Any = self.m.mlx_init()
        self._win_ptr: Any = self.m.mlx_new_window(
            self._mlx_ptr,
            self._width,
            self._height,
            "A-Maze-Ing"
        )
        self._img_ptr = self.m.mlx_new_image(
            self._mlx_ptr,
            self._width,
            self._height
        )

        data_info = self.m.mlx_get_data_addr(self._img_ptr)
        pixel_array_type = ctypes.c_uint32 * (
            self._width * self._height
        )
        self.pixel_buffer = pixel_array_type.from_buffer(data_info[0])
        self.screen: np.ndarray[Any, np.dtype[np.uint32]] = (
            np.frombuffer(
                self.pixel_buffer,
                dtype=np.uint32
            ).reshape((self._height, self._width))
        )

        self.setup_hooks()

    @property
    def width(self) -> int:
        """Return the window width in pixels.

        Returns:
            The current window width.
        """
        return self._width

    @property
    def height(self) -> int:
        """Return the window height in pixels.

        Returns:
            The current window height.
        """
        return self._height

    @property
    def img_ptr(self) -> Any:
        """Return the MLX image pointer.

        Returns:
            The MLX image pointer.
        """
        return self._img_ptr

    def setup_hooks(self) -> None:
        """Register keyboard, window, and render-loop callbacks."""
        self.m.mlx_hook(
            self._win_ptr,
            2,
            1 << 0,
            self.key_press,
            None
        )
        self.m.mlx_hook(
            self._win_ptr,
            3,
            1 << 1,
            self.key_release,
            None
        )
        self.m.mlx_hook(
            self._win_ptr,
            17,
            0,
            self.close,
            None
        )
        self.m.mlx_loop_hook(
            self._mlx_ptr,
            self.render_loop_callback,
            None
        )

    def key_press(
        self,
        keycode: int,
        param: Optional[Any] = None
    ) -> None:
        """Handle a keyboard key press.

        Args:
            keycode: Numeric code of the pressed key.
            param: Optional callback parameter supplied by MLX.
        """
        if keycode in (65307, 53):
            self.close()
            return

        if keycode in (109, 65289, 46, 48):
            self.active_mode = (
                "3D" if self.active_mode == "2D" else "2D"
            )
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
        param: Optional[Any] = None
    ) -> None:
        """Handle a keyboard key release.

        Args:
            keycode: Numeric code of the released key.
            param: Optional callback parameter supplied by MLX.
        """
        self.keys_pressed.discard(keycode)

    def render_loop_callback(self, param: object) -> int:
        """Render one frame from the MLX loop callback.

        Args:
            param: Callback parameter supplied by MLX.

        Returns:
            Zero to continue the MLX event loop.
        """
        self.render_frame()
        return 0

    def process_movement(self) -> None:
        """Process currently pressed movement and rotation keys."""
        if not self.player or self.active_mode != "3D":
            return

        move_speed = 0.05
        rot_speed = 0.04

        if 119 in self.keys_pressed:
            self.player.move_forward(move_speed)
        if 115 in self.keys_pressed:
            self.player.move_backward(move_speed)
        if 97 in self.keys_pressed:
            self.player.move_left(move_speed)
        if 100 in self.keys_pressed:
            self.player.move_right(move_speed)

        if 65361 in self.keys_pressed or 123 in self.keys_pressed:
            self.player.rotate(-rot_speed)
        if 65363 in self.keys_pressed or 124 in self.keys_pressed:
            self.player.rotate(rot_speed)

    def draw_menu(self) -> None:
        """Draw the current mode and available controls."""
        colour = 0x00FFFFFF

        self.m.mlx_string_put(
            self._mlx_ptr,
            self._win_ptr,
            self.width - 250,
            self.height - 140,
            colour,
            f"ACTUAL MODE: {self.active_mode}"
        )

        if self.active_mode == "2D":
            self.m.mlx_string_put(
                self._mlx_ptr,
                self._win_ptr,
                self.width - 300,
                self.height - 120,
                colour,
                "[M/TAB] Change mode (2D/3D)"
            )
            self.m.mlx_string_put(
                self._mlx_ptr,
                self._win_ptr,
                self.width - 300,
                self.height - 100,
                colour,
                "[U] Regenerate"
            )
            self.m.mlx_string_put(
                self._mlx_ptr,
                self._win_ptr,
                self.width - 300,
                self.height - 80,
                colour,
                "[I] Show Route"
            )
            self.m.mlx_string_put(
                self._mlx_ptr,
                self._win_ptr,
                self.width - 300,
                self.height - 60,
                colour,
                "[O] Animate"
            )
            self.m.mlx_string_put(
                self._mlx_ptr,
                self._win_ptr,
                self.width - 300,
                self.height - 40,
                colour,
                "[P] Change Theme"
            )

        if self.active_mode == "3D":
            self.m.mlx_string_put(
                self._mlx_ptr,
                self._win_ptr,
                self.width - 270,
                self.height - 120,
                colour,
                "[W/A/S/D] Move  [< >] Rotate"
            )

    def render_frame(self, *args: object) -> None:
        """Render the current application frame.

        Args:
            *args: Optional callback arguments supplied by MLX.
        """
        self.process_movement()

        if self.active_mode == "2D" and self._renderer_2d:
            self._renderer_2d.update_animation()
            self._renderer_2d.render_frame(self.screen)

        elif self.active_mode == "3D" and self._renderer_3d:
            self._renderer_3d.render_frame(self.screen)

        self.m.mlx_put_image_to_window(
            self._mlx_ptr,
            self._win_ptr,
            self._img_ptr,
            0,
            0
        )

        self.draw_menu()
        self.m.mlx_do_sync(self._mlx_ptr)

    def close(self, param: Optional[Any] = None) -> None:
        """Destroy MLX resources and terminate the application.

        Args:
            param: Optional callback parameter supplied by MLX.
        """
        if self._img_ptr:
            self.m.mlx_destroy_image(
                self._mlx_ptr,
                self._img_ptr
            )

        if self._win_ptr:
            self.m.mlx_destroy_window(
                self._mlx_ptr,
                self._win_ptr
            )

        self.m.mlx_release(self._mlx_ptr)
        os._exit(0)

    def run(self) -> None:
        """Start the MLX event loop."""
        self.m.mlx_loop_hook(
            self._mlx_ptr,
            self.render_frame,
            None
        )
        self.m.mlx_loop(self._mlx_ptr)


def mlx_display(
    entry: tuple[int, int],
    ex: tuple[int, int],
    path_str: str
) -> None:
    """Initialize the maze display and start the application.

    Args:
        entry: Logical maze entry coordinate.
        ex: Logical maze exit coordinate.
        path_str: Logical solution path.
    """
    physical_entry = (
        entry[1] * 2 + 1,
        entry[0] * 2 + 1
    )

    physical_ex = (
        ex[1] * 2 + 1,
        ex[0] * 2 + 1
    )

    maze_model = MazeModel(
        "utilities/processed_map.npy",
        physical_entry,
        physical_ex
    )

    player = Player(maze_model)
    generator = MazeGenerator()

    renderer_2d = MazeRenderer(
        model=maze_model,
        visited_steps=[],
        final_path=[]
    )

    renderer_3d = EngineRenderer(
        model=maze_model,
        player=player,
        width=1200,
        height=800
    )

    controller = MazeController(
        renderer_2d,
        generator,
        player,
        renderer_3d
    )

    window = mlx_buffer(
        width=1200,
        height=800,
        renderer_2d=renderer_2d,
        renderer_3d=renderer_3d,
        maze_ctrl=controller,
        player=player
    )

    if window.maze_ctrl is None:
        raise RuntimeError("Maze controller was not initialized.")

    window.maze_ctrl.gen()
    window.maze_ctrl.animation()
    window.run()
