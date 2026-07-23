from mlx import Mlx
import sys


def mymouse(button, x, y):
    print(f"Got mouse event! button {button} at {x}, {y}.")


def mykey(keynum, stuff):
    print(f"Got key {keynum}")
    if keynum == 32:
        m.mlx_mouse_hook(win_ptr, None, None)
    elif keynum == 65307:
        m.mlx_destroy_window(mlx_ptr, win_ptr)
        sys.exit(0)


m = Mlx()

mlx_ptr = m.mlx_init()
win_ptr = m.mlx_new_window(mlx_ptr, 1920, 1080, "test")

m.mlx_mouse_hook(win_ptr, mymouse, None)
m.mlx_key_hook(win_ptr, mykey, None)

m.mlx_string_put(mlx_ptr, win_ptr, 0, 800, 255, "-" * 1920)

m.mlx_loop(mlx_ptr)