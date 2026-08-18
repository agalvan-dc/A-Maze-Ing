import os
import random
import math
import ctypes
import numpy as np
from mlx import Mlx
from typing import Optional
from .renderer import MazeRenderer, AnimationState
from structure import MazeSolver, MazeModel, MazeGenerator
from display.terminal_display import bin_maze
from engine.Player import Player
from engine.buffer import EngineRenderer


def random_color() -> int:
    r = random.randint(100, 255)
    g = random.randint(100, 255)
    b = random.randint(100, 255)
    return (0xFF << 24) | (r << 16) | (g << 8) | b


class MazeController:
    def __init__(self,
                 renderer: MazeRenderer,
                 generator: MazeGenerator,
                 player: Optional[Player] = None,
                 renderer_3d: Optional[EngineRenderer] = None) -> None:
        self.renderer = renderer
        self.generator = generator
        self.player = player
        self.renderer_3d = renderer_3d

    def gen(self) -> None:
        config_data = self.generator.get_config()
        self.generator.generate_maze(config_data, "basic")

        filepath = "utilities/maze_output.txt"
        logical_entry, logical_ex, path_str = bin_maze(filepath)

        self.renderer.model.grid = np.load(
            "utilities/processed_map.npy"
        )

        self.renderer.model.rows, self.renderer.model.cols = (
            self.renderer.model.grid.shape
        )

        physical_entry = (
            logical_entry[1] * 2 + 1,
            logical_entry[0] * 2 + 1
        )

        physical_ex = (
            logical_ex[1] * 2 + 1,
            logical_ex[0] * 2 + 1
        )

        self.renderer.model.start = physical_entry
        self.renderer.model.end = physical_ex

        new_solver = MazeSolver(
            self.renderer.model,
            logical_entry,
            logical_ex
        )

        logical_visited = new_solver.get_visited()

        visited_set = set(logical_visited)
        physical_visited = set()

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

        physical_path = []

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
        self.renderer.state = AnimationState.FINISHED
        self.renderer.path_index = len(self.renderer.final_path)

    def animation(self) -> None:
        self.renderer.step_index = 0
        self.renderer.path_index = 0
        self.renderer.state = AnimationState.EXPLORING

    def rand_color(self) -> None:
        self.renderer.COLOR_BG = random_color()
        self.renderer.COLOR_WALL = random_color()
        self.renderer.COLOR_PATH = random_color()
        self.renderer.COLOR_VISITED = random_color()


class mlx_buffer:
    def __init__(self,
                 width: int = 800,
                 height: int = 600,
                 renderer_2d: Optional[MazeRenderer] = None,
                 renderer_3d: Optional[EngineRenderer] = None,
                 maze_ctrl: Optional[MazeController] = None,
                 player: Optional[Player] = None) -> None:
        self._width = width
        self._height = height
        self._img_ptr = None

        self.maze_ctrl = maze_ctrl
        self._renderer_2d = renderer_2d
        self._renderer_3d = renderer_3d
        self.player = player

        self.active_mode = "2D"
        self._ignore_next_mouse: bool = False
        self.keys_pressed: set[int] = set()

        self.m = Mlx()
        self._mlx_ptr = self.m.mlx_init()
        self._win_ptr = self.m.mlx_new_window(self._mlx_ptr,
                                              self._width,
                                              self._height,
                                              "A-Maze-Ing")
        self._img_ptr = self.m.mlx_new_image(self._mlx_ptr,
                                             self._width,
                                             self._height)

        data_info = self.m.mlx_get_data_addr(self._img_ptr)
        PixelArrayType = ctypes.c_uint32 * (self._width * self._height)
        self.pixel_buffer = PixelArrayType.from_buffer(data_info[0])
        self.screen = np.frombuffer(self.pixel_buffer,
                                    dtype=np.uint32).reshape((self._height,
                                                              self._width))

        self.setup_hooks()

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    @property
    def img_ptr(self):
        return self._img_ptr

    def setup_hooks(self) -> None:
        self.m.mlx_hook(self._win_ptr, 2, 1 << 0, self.key_press, None)
        self.m.mlx_hook(self._win_ptr, 3, 1 << 1, self.key_release, None)
        self.m.mlx_hook(self._win_ptr, 17, 0, self.close, None)
        self.m.mlx_loop_hook(self._mlx_ptr, self.render_loop_callback, None)

    def key_press(self, keycode: int, param=None) -> None:
        if keycode in (65307, 53):
            self.close()
            return
        if keycode in (109, 65289, 46, 48):
            self.active_mode = "3D" if self.active_mode == "2D" else "2D"
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
        self.keys_pressed.discard(keycode)

    def render_loop_callback(self, param: object) -> int:
        self.render_frame()
        return 0

    def process_movement(self) -> None:
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
        colour = 0x00FFFFFF

        self.m.mlx_string_put(self._mlx_ptr, self._win_ptr,
                              self.width - 250, self.height - 140, colour,
                              f"ACTUAL MODE: {self.active_mode}")
        if self.active_mode == "2D":
            self.m.mlx_string_put(self._mlx_ptr, self._win_ptr,
                                  self.width - 300, self.height - 120, colour,
                                  "[M/TAB] Change mode (2D/3D)")
            self.m.mlx_string_put(self._mlx_ptr, self._win_ptr,
                                  self.width - 300, self.height - 100, colour,
                                  "[U] Regenerate")
            self.m.mlx_string_put(self._mlx_ptr, self._win_ptr,
                                  self.width - 300, self.height - 80, colour,
                                  "[I] Show Route")
            self.m.mlx_string_put(self._mlx_ptr, self._win_ptr,
                                  self.width - 300, self.height - 60, colour,
                                  "[O] Animate")
            self.m.mlx_string_put(self._mlx_ptr, self._win_ptr,
                                  self.width - 300, self.height - 40, colour,
                                  "[P] Change Theme")

        if self.active_mode == "3D":
            self.m.mlx_string_put(self._mlx_ptr, self._win_ptr,
                                  self.width - 270, self.height - 120,
                                  colour, "[W/A/S/D] Move  [< >] Rotate")

    def render_frame(self, *args) -> None:
        self.process_movement()

        if self.active_mode == "2D" and self._renderer_2d:
            self._renderer_2d.update_animation()
            self._renderer_2d.render_frame(self.screen)

        elif self.active_mode == "3D" and self._renderer_3d:
            self._renderer_3d.render_frame(self.screen)

        self.m.mlx_put_image_to_window(self._mlx_ptr, self._win_ptr,
                                       self._img_ptr, 0, 0)

        self.draw_menu()
        self.m.mlx_do_sync(self._mlx_ptr)

    def close(self, param=None) -> None:
        if self._img_ptr:
            self.m.mlx_destroy_image(self._mlx_ptr, self._img_ptr)
        if self._win_ptr:
            self.m.mlx_destroy_window(self._mlx_ptr, self._win_ptr)
        self.m.mlx_release(self._mlx_ptr)
        os._exit(0)

    def run(self) -> None:
        self.m.mlx_loop_hook(self._mlx_ptr, self.render_frame, None)
        self.m.mlx_loop(self._mlx_ptr)


def mlx_display(entry: tuple[int, int],
                ex: tuple[int, int],
                path_str: str) -> None:

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

    maze_solver = MazeSolver(
        maze_model,
        entry,
        ex
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

    window.maze_ctrl.gen()
    window.maze_ctrl.animation()
    window.run()
