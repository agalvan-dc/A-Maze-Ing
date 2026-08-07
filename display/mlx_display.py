import numpy as np
import sys
import random
from mlx import Mlx
from typing import Optional
from collections.abc import Callable
from .renderer import MazeRenderer, AnimationState
from ..structure import MazeSolver, MazeModel
from .terminal_display import bin_maze
from ..engine.Player import Player
from ..engine.buffer import EngineRenderer


def random_color() -> int:
    r = random.randint(100, 255)
    g = random.randint(100, 255)
    b = random.randint(100, 255)

    return (r << 16) | (g << 8) | b

class MazeGenerator:
    def __init__(self, renderer: MazeRenderer) -> None:
        self.renderer = renderer

    def gen(self) -> None:
        self.renderer.model.generate_new_maze()
        self.renderer.visited_steps = []
        self.renderer.final_path = []
        self.renderer.state = AnimationState.EXPLORING

    def show(self) -> None:
        self.renderer.state = AnimationState.FINISHED
        self.renderer.path_index = len(self.renderer.final_path)

    def animation(self) -> None:
        self.renderer.step_index = 0
        self.renderer.path_index = 0
        self.renderer.state = AnimationState.EXPLORING

    def rand_color(self) -> None:
        self.renderer.COLOR_BG = random_color()


class mlx_buffer:
    def __init__(self,
                 width: int = 800,
                 height: int = 600,
                 renderer_2d = None,
                 renderer_3d = None,
                 maze_gen: Optional[MazeGenerator] = None,
                 player = None
                 ) -> None:
        self._width = width
        self._height = height
        self._img_ptr = None

        self._maze_gen = maze_gen
        self._renderer_2d = renderer_2d
        self._renderer_3d = renderer_3d
        self.player = Player

        self.active_mode = "2D"
        self._last_mouse_x = self._width // 2
        self.keys_pressed: set[int] = set()

        self.m = Mlx()
        self._mlx_ptr = self.m.mlx_init()
        self._win_ptr = self.m.mlx_new_window(self._mlx_ptr,
                              self._width,
                              self._height, "A-Maze-Ing")
        self._img_ptr = self.m.mlx_new_image(self._mlx_ptr,
                                             self._width,
                                             self._height)
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
        self.m.mlx_hook(self._win_ptr, 6, 1 << 6, self.mouse_move, None)

    def key_press(self, keycode: int, param=None) -> None:
        if keycode == 65307:
            self.close()
            return 
        if keycode in (109, 65289):
            self.active_mode = "3D" if self.active_mode == "2D" else "2D"
            return
        if self._maze_gen:
            match keycode:
                case 117: #maze regeneration
                    self._maze_gen.gen()
                case 105:  #show shortest path
                    self._maze_gen.show()
                case 111:  #Show exploration animation
                    self._maze_gen.animation()
                case 112:  #change theme
                    self._maze_gen.rand_color()
        self.keys_pressed.add(keycode)

    def key_release(self, keycode: int, param=None) -> None:
        self.keys_pressed.discard(keycode)

    def mouse_move(self, x: int, y: int, param=None) -> None:
        sens = 0.03
        if self.active_mode != "3D" or not self.player:
            return

        delta_x = x - self._last_mouse_x
        if abs(delta_x) < 100:
            self.player.rotate(delta_x * sens)
        self.last_mouse_x = x

    def process_movement(self) -> None:
        if not self.player or self.active_mode != "3D":
            return

        move_speed = 0.05
        if 119 in self.keys_pressed or 65362 in self.keys_pressed:
            self.player.move_forward(move_speed)
        if 115 in self.keys_pressed or 65364 in self.keys_pressed:
            self.player.move_backward(move_speed)
        if 97 in self.keys_pressed or 65361 in self.keys_pressed:
            self.player.move_left(move_speed)
        if 100 in self.keys_pressed or 65363 in self.keys_pressed:
            self.player.move_right(move_speed)

    def draw_menu(self) -> None:
        colour = 0xFFFFFF
        self.m.mlx_string_put(self._mlx_ptr, self._win_ptr, 10, 20, colour, f"ACTUAL MODE: {self.active_mode}")
        self.m.mlx_string_put(self._mlx_ptr, self._win_ptr, 10, 40, colour, "[M/TAB] Change mode (2D/3D)")
        self.m.mlx_string_put(self._mlx_ptr, self._win_ptr, 10, 60, colour, "[U] Regenerate  [I] Show Route")
        self.m.mlx_string_put(self._mlx_ptr, self._win_ptr, 10, 80, colour, "[O] Animate     [P] Change Theme")

        if self.active_mode == "3D":
            self.m.mlx_string_put(self._mlx_ptr, self._win_ptr, 10, 100, colour, "[W/A/S/D] Move")

    def render_frame(self) -> None:
        self.process_movement()

        if self.active_mode == "2D" and self._renderer_2d:
            self._renderer_2d.update_animation(self)

        elif self.active_mode == "3D" and self._renderer_3d:
            self._renderer_3d.render_frame(self)

        self.m.mlx_put_image_to_window(self._mlx_ptr, self._win_ptr,
                                       self._img_ptr, 0, 0)
        self.draw_menu()

    def close(self, param=None) -> None:
        if self._img_ptr:
            self.m.mlx_destroy_image(self._mlx_ptr, self._img_ptr)
        if self._win_ptr:
            self.m.mlx_destroy_window(self._mlx_ptr, self._win_ptr)
        self.m.mlx_release(self._mlx_ptr)
        sys.exit(0)

    def run(self) -> None:
        self.m.mlx_loop_hook(self._mlx_ptr, self.render_frame, None)
        self.m.mlx_loop(self._mlx_ptr)


def mlx_display_main(entry: tuple, ex: tuple, path_str: str) -> None:
    maze_model = MazeModel("processed_map.npy", entry, ex)
    maze_solver = MazeSolver(maze_model)
    player = Player(maze_model)

    renderer_2d = MazeRenderer(
        model=maze_model, 
        visited_steps=maze_solver.get_visited(),
        final_path=maze_solver.get_path()
    )
    renderer_3d = EngineRenderer(model=maze_model, player=player)
    generator = MazeGenerator(renderer_2d)

    window = mlx_buffer(
        width=800, 
        height=600, 
        renderer_2d=renderer_2d,
        renderer_3d=renderer_3d,
        maze_gen=generator,
        player=player
    )

    window.run()
