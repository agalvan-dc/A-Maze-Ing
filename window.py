import ctypes
from typing import Callable, Optional
from mlx import Mlx  # Ajusta la importación según tu librería MLX


class ResponsiveBuffer:
    def __init__(self,
                 initial_width: int = 800,
                 initial_height: int = 600,
                 render: Optional[Callable[['ResponsiveBuffer'], None]] = None
                 ) -> None:
        self.m = Mlx()
        self.mlx_ptr = self.m.mlx_init()
        self.width = initial_width
        self.height = initial_height
        self.render_callback = render

        self.win_ptr = self.m.mlx_new_window(
            self.mlx_ptr, self.width, self.height, "Maze Solver MLX"
        )

        self.img_ptr = None
        self.update_buffer(self.width, self.height)

        self.m.mlx_hook(self.win_ptr, 22, 0, self.on_resize, None)
        self.m.mlx_expose_hook(self.win_ptr, self.on_resize, None)

        self.m.mlx_key_hook(self.win_ptr, self.on_key_press, None)
        self.m.mlx_hook(self.win_ptr, 17, 0, self.close, None)

    def update_buffer(self, new_width: int, new_height: int) -> None:
        if self.img_ptr:
            self.m.mlx_destroy_image(self.mlx_ptr, self.img_ptr)

        self.width = new_width
        self.height = new_height
        self.img_ptr = self.m.mlx_new_image(
            self.mlx_ptr, self.width, self.height
        )

    def render_frame(self) -> None:
        if self.render_callback:
            self.render_callback(self)

        self.m.mlx_put_image_to_window(
            self.mlx_ptr, self.win_ptr, self.img_ptr, 0, 0
        )

    def on_resize(self, param) -> None:
        self.update_buffer(self.width, self.height)
        self.render_frame()

    def on_key_press(self, keycode: int, param) -> None:
        if keycode == 65307:  # Tecla ESC
            self.close(param)

    def close(self, param=None) -> None:
        if self.img_ptr:
            self.m.mlx_destroy_image(self.mlx_ptr, self.img_ptr)
        self.m.mlx_destroy_window(self.mlx_ptr, self.win_ptr)
        self.m.mlx_loop_exit(self.mlx_ptr)

    def run(self, update_loop_callback=None) -> None:
        if update_loop_callback:
            self.m.mlx_loop_hook(self.mlx_ptr, update_loop_callback, None)

        self.render_frame()
        self.m.mlx_loop(self.mlx_ptr)
        self.m.mlx_release(self.mlx_ptr)


# Matriz de 5x7 que define los píxeles del "42"
MATRIX_42 = [
    [1, 0, 1,  0,  1, 1, 1],
    [1, 0, 1,  0,  0, 0, 1],
    [1, 1, 1,  0,  1, 1, 1],
    [0, 0, 1,  0,  1, 0, 0],
    [0, 0, 1,  0,  1, 1, 1],
]


def render_42_logo(buffer: ResponsiveBuffer) -> None:
    """Callback de renderizado: Dibuja un logo de 42 centrado y responsivo."""
    COLOR_BG = 0x1E1E2E      # Fondo gris oscuro
    COLOR_42 = 0x00D68F      # Verde Cyan 42

    data_ptr, bpp, size_line, endian = buffer.m.mlx_get_data_addr(
        buffer.img_ptr
    )
    pixels = ctypes.cast(data_ptr, ctypes.POINTER(ctypes.c_uint32))
    stride = size_line // 4

    # 1. Rellenar fondo completo
    for y in range(buffer.height):
        row_offset = y * stride
        for x in range(buffer.width):
            pixels[row_offset + x] = COLOR_BG

    # 2. Calcular escalado responsivo (~50% del tamaño de pantalla)
    rows = len(MATRIX_42)
    cols = len(MATRIX_42[0])

    cell_w = (buffer.width * 0.5) / cols
    cell_h = (buffer.height * 0.5) / rows
    cell_size = max(1.0, min(cell_w, cell_h))

    # 3. Calcular offsets para centrar
    offset_x = (buffer.width - (cols * cell_size)) / 2
    offset_y = (buffer.height - (rows * cell_size)) / 2

    # 4. Pintar los bloques del "42"
    for r in range(rows):
        for c in range(cols):
            if MATRIX_42[r][c] == 1:
                x_start = int(offset_x + c * cell_size)
                y_start = int(offset_y + r * cell_size)
                size = int(cell_size)

                y_end = min(y_start + size, buffer.height)
                x_end = min(x_start + size, buffer.width)

                for y in range(max(0, y_start), y_end):
                    r_off = y * stride
                    for x in range(max(0, x_start), x_end):
                        pixels[r_off + x] = COLOR_42


if __name__ == "__main__":
    app = ResponsiveBuffer(
        initial_width=800,
        initial_height=600,
        render=render_42_logo
    )
    app.run()
