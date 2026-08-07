import numpy as np
import sys
import random
from mlx import Mlx
from typing import Optional
from collections.abc import Callable
from .renderer import MazeRenderer, AnimationState
from ..structure import MazeSolver, MazeModel
from .terminal_display import bin_maze


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
                 renderer: Optional[Callable[['mlx_buffer'], None]] = None,
                 maze_gen: Optional[MazeGenerator] = None
                 ) -> None:
        self._width = width
        self._height = height
        self._img_ptr = None
        self._maze_gen = maze_gen
        self.m = Mlx()
        self._mlx_ptr = self.m.mlx_init()
        self._renderer = renderer

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
        self.m.mlx_key_hook(self._win_ptr, self.key_events, None)
        self.m.mlx_hook(self._win_ptr, 17, 0, self.close, None)

    def key_events(self, keycode: int, param=None) -> None:
        if keycode == 65307:
            self.close()
            return 
        elif not self._maze_gen:
            return 

        match keycode:
            case 117: #maze regeneration
                self._maze_gen.gen()
            case 105:  #show shortest path
                self._maze_gen.show()
            case 111:  #Show exploration animation
                self._maze_gen.animation()
            case 112:  #change theme
                self._maze_gen.rand_color()

        self.render_frame()

    def render_frame(self) -> None:
        if self._renderer:
            self._renderer(self)
            self.m.mlx_put_image_to_window(self._mlx_ptr, self._win_ptr,
                                           self._img_ptr, 0, 0)

    def close(self, param=None) -> None:
        if self._img_ptr:
            self.m.mlx_destroy_image(self._mlx_ptr, self._img_ptr)
        if self._win_ptr:
            self.m.mlx_destroy_window(self._mlx_ptr, self._win_ptr)
        self.m.mlx_release(self._mlx_ptr)
        sys.exit(0)

    def run(self, update_loop_callback=None) -> None:
        if update_loop_callback:
            self.m.mlx_loop_hook(self._mlx_ptr, update_loop_callback, self)

        self.render_frame()
        self.m.mlx_loop(self._mlx_ptr)

def mlx_2d_display(entry: tuple, ex: tuple, path_str: str) -> None:
    maze_model = MazeModel("processed_map.npy", entry, ex)
    maze_solver = MazeSolver(maze_model)

    renderer = MazeRenderer(
        model=maze_model, 
        visited_steps=maze_solver.get_visited(),
        final_path=maze_solver.get_path()
    )
    generator = MazeGenerator(renderer)

    window = mlx_buffer(
        width=800, 
        height=600, 
        renderer=renderer.render_frame, 
        maze_gen=generator
    )

    window.run(update_loop_callback=renderer.update_animation)
