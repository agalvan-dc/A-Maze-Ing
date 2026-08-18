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
    """Generates a random color in a 32-bit integer format.

    Returns:
        An integer representing an alpha-channel compatible hexadecimal color.
    """
    r = random.randint(100, 255)
    g = random.randint(100, 255)
    b = random.randint(100, 255)
    return (0xFF << 24) | (r << 16) | (g << 8) | b


class MazeController:
    """Manages user inputs, states, and control triggers for the maze simulation.

    Attributes:
        renderer: MazeRenderer instance responsible for 2D rendering.
        generator: MazeGenerator instance responsible for procedurally generating mazes.
        player: Player instance managing 3D movement and camera rotation.
        renderer_3d: EngineRenderer instance managing the raycaster engine and pseudo-3D views.
    """

    def __init__(self,
                 renderer: MazeRenderer,
                 generator: MazeGenerator,
                 player: Optional[Player] = None,
                 renderer_3d: Optional[EngineRenderer] = None) -> None:
        """Initializes the maze controller with rendering, generation, and player components.

        Args:
            renderer: The 2D maze renderer instance.
            generator: The maze generator instance.
            player: The player state instance for 3D navigation. Defaults to None.
            renderer_3d: The 3D raycasting engine instance. Defaults to None.
        """
        self.renderer = renderer
        self.generator = generator
        self.player = player
        self.renderer_3d = renderer_3d

    def gen(self) -> None:
        """Generates a brand new maze, solves it, and re-links all view states.

        Triggers procedural creation, loads the processed map, solves the routing,
        updates 2D/3D render paths, and resets player starting vectors.
        """
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
        """Toggles the visibility state of the solution path on the display."""
        if self.renderer.path_index > 0:
            self.renderer.path_index = 0
        else:
            self.renderer.path_index = len(self.renderer.final_path)
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
    """Buffer class handling the display screen buffer, 2D/3D renderers, and events.

    Attributes:
        width: Buffer width, defaults to 800.
        height: Buffer height, defaults to 600.
        renderer_2d: Renders maze in a 2D format.
        renderer_3d: Renders maze with a raycaster engine.
        maze_ctrl: Handles keyboard event options.
        player: Handles 3D player movement and rotation.
    """

    def __init__(self,
                 width: int = 800,
                 height: int = 600,
                 renderer_2d: Optional[MazeRenderer] = None,
                 renderer_3d: Optional[EngineRenderer] = None,
                 maze_ctrl: Optional[MazeController] = None,
                 player: Optional[Player] = None) -> None:
        """Initializes the window buffer, graphic contexts, pixel arrays, and event hooks.

        Args:
            width: Width of the display area in pixels. Defaults to 800.
            height: Height of the display area in pixels. Defaults to 600.
            renderer_2d: Optional 2D render instance. Defaults to None.
            renderer_3d: Optional 3D engine render instance. Defaults to None.
            maze_ctrl: Optional controller instance for events. Defaults to None.
            player: Optional player movement configuration. Defaults to None.
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
        self._win_ptr = self.m.mlx_new_window(self._mlx_ptr,
                                              self._width + self._ui_width,
                                              self._height,
                                              "A-Maze-Ing")
        self._img_ptr = self.m.mlx_new_image(self._mlx_ptr,
                                             self._width,
                                             self._height)
        self._ui_bg_ptr = self.m.mlx_new_image(self._mlx_ptr,
                                                self._ui_width,
                                                self._height)

        data_info = self.m.mlx_get_data_addr(self._img_ptr)
        PixelArrayType = ctypes.c_uint32 * (self._width * self._height)
        self.pixel_buffer = PixelArrayType.from_buffer(data_info[0])
        self.screen = np.frombuffer(self.pixel_buffer,
                                    dtype=np.uint32).reshape((self._height,
                                                              self._width))

        self.setup_hooks()
        self.draw_menu()

        if self._renderer_3d:
            tex_wall = self.load_xpm_texture("utilities/wall.xpm")
            tex_floor = self.load_xpm_texture("utilities/floor.xpm")
            tex_path = self.load_xpm_texture("utilities/path.xpm")
            self._renderer_3d.set_textures(tex_wall, tex_floor, tex_path)

    @property
    def width(self) -> int:
        """Gets the public width dimension of the active screen buffer."""
        return self._width

    @property
    def height(self) -> int:
        """Gets the public height dimension of the active screen buffer."""
        return self._height

    @property
    def img_ptr(self):
        """Gets the underlying image pointer reference used by the graphics library."""
        return self._img_ptr

    def setup_hooks(self) -> None:
        """Sets keyboard and window hooks for event-oriented programming."""
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

    def key_press(self, keycode: int, param=None) -> None:
        """Manages pressing keys and maps them to their respective functions.

        Args:
            keycode: The integer representation of the key pressed.
            param: Empty parameter required by the MLX C function prototype.
        """
        if keycode in (65307, 53):
            self.close()
            return

        if keycode in (109, 65289, 46, 48):
            self.active_mode = "3D" if self.active_mode == "2D" else "2D"
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

    def key_release(self, keycode: int, param=None) -> None:
        """Manages key releases, removing the key from the active pressed set.

        Args:
            keycode: The integer representation of the key released.
            param: Empty parameter required by the MLX C function prototype.
        """
        self.keys_pressed.discard(keycode)

    def process_movement(self) -> None:
        """Calculates and applies player translation and rotation in 3D mode."""
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
            
    def load_xpm_texture(self, filepath: str) -> np.ndarray:
        """Loads an XPM image asset using MLX bindings and converts it to a Numpy uint32 array.

        Args:
            filepath: Target file path of the XPM image asset.

        Returns:
            A 2D uint32 Numpy array representing spatial image color values.
        """
        img_ptr, w, h = self.m.mlx_xpm_file_to_image(self._mlx_ptr, filepath)

        if not img_ptr:
            fallback = np.full((64, 64), 0xFFFF00FF, dtype=np.uint32)
            fallback[::2, ::2] = 0xFF000000
            fallback[1::2, 1::2] = 0xFF000000
            return fallback

        data_info = self.m.mlx_get_data_addr(img_ptr)
        PixelArrayType = ctypes.c_uint32 * (w * h)
        pixel_buffer = PixelArrayType.from_buffer(data_info[0])
        tex_array = np.frombuffer(pixel_buffer, dtype=np.uint32).reshape((h, w)).copy()

        self.m.mlx_destroy_image(self._mlx_ptr, img_ptr)
        return tex_array

    def draw_menu(self) -> None:
        """Renders the static text interface onto the dedicated side panel."""
        colour = 0x00FFFFFF
        base_x = self._width + 20
        base_y = 50

        self.m.mlx_put_image_to_window(self._mlx_ptr,
                                       self._win_ptr,
                                       self._ui_bg_ptr,
                                       self._width, 0)

        self.m.mlx_string_put(self._mlx_ptr, self._win_ptr,
                              base_x, base_y, colour,
                              f"Actual Mode: {self.active_mode}")
        self.m.mlx_string_put(self._mlx_ptr, self._win_ptr,
                              base_x, base_y + 30, colour,
                              "-------------------------")

        if self.active_mode == "2D":
            self.m.mlx_string_put(self._mlx_ptr, self._win_ptr,
                                  base_x, base_y + 60, colour,
                                  "[M/TAB] Change mode")
            self.m.mlx_string_put(self._mlx_ptr, self._win_ptr,
                                  base_x, base_y + 90, colour,
                                  "[U] Regen maze")
            self.m.mlx_string_put(self._mlx_ptr, self._win_ptr,
                                  base_x, base_y + 120, colour,
                                  "[I] Show / Hide Path")
            self.m.mlx_string_put(self._mlx_ptr, self._win_ptr,
                                  base_x, base_y + 150, colour,
                                  "[O] Animate")
            self.m.mlx_string_put(self._mlx_ptr, self._win_ptr,
                                  base_x, base_y + 180, colour,
                                  "[P] Change theme")
        else:
            self.m.mlx_string_put(self._mlx_ptr, self._win_ptr,
                                  base_x, base_y + 60, colour,
                                  "[W/A/S/D] Move")
            self.m.mlx_string_put(self._mlx_ptr, self._win_ptr,
                                  base_x, base_y + 90, colour,
                                  "[< / >]   Rotate cam")

    def render_frame(self, param=None) -> int:
        """Main rendering loop callback. Evaluates states and updates the window buffer.

        Args:
            param: Empty parameter required by the MLX loop hook prototype.

        Returns:
            int: Always returns 0.
        """
        self.process_movement()

        if self.active_mode == "2D" and self._renderer_2d:
            self._renderer_2d.update_animation()
            self._renderer_2d.render_frame(self.screen)
        elif self.active_mode == "3D" and self._renderer_3d:
            self._renderer_3d.render_frame(self.screen)

        self.m.mlx_put_image_to_window(self._mlx_ptr,
                                       self._win_ptr,
                                       self._img_ptr, 0, 0)

        self.m.mlx_do_sync(self._mlx_ptr)
        return 0

    def close(self, param=None) -> None:
        """Cleans up memory allocations and safely terminates the application.

        Args:
            param: Empty parameter required by the MLX hook prototype.
        """
        if self._ui_bg_ptr:
            self.m.mlx_destroy_image(self._mlx_ptr, self._ui_bg_ptr)
        if self._img_ptr:
            self.m.mlx_destroy_image(self._mlx_ptr, self._img_ptr)
        if self._win_ptr:
            self.m.mlx_destroy_window(self._mlx_ptr, self._win_ptr)
        self.m.mlx_release(self._mlx_ptr)
        os._exit(0)

    def run(self) -> None:
        """Registers the main render loop and starts the MLX event listener."""
        self.m.mlx_loop_hook(self._mlx_ptr, self.render_frame, None)
        self.m.mlx_loop(self._mlx_ptr)


def mlx_display(entry: tuple[int, int], ex: tuple[int, int],
                path_str: str) -> None:
    """Entry point for the graphical simulation initialization.

    Args:
        entry: A tuple containing the (row, col) coordinates for the maze start.
        ex: A tuple containing the (row, col) coordinates for the maze exit.
        path_str: A string representation of the parsed solution path.
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
