import os
from mlx import Mlx
from PIL import Image

class ImageRenderer:
    """Renderer que estira y adapta la imagen exactamente al tamaño de la ventana."""
    
    def __init__(self, image_filename: str):
        self.image_filename = image_filename
        self.temp_file = "temp_render.png"
        self.img_ptr = None

    def prepare_image(self, m_instance: Mlx, mlx_ptr, win_w: int, win_h: int):
        """Redimensiona la imagen para cubrir el 100% de la ventana."""
        if not os.path.exists(self.image_filename):
            print(f"[ERROR] No existe el archivo: {self.image_filename}")
            return

        # 1. Cargar imagen original
        img = Image.open(self.image_filename).convert("RGBA")
        
        resample_filter = Image.Resampling.LANCZOS if hasattr(Image, 'Resampling') else Image.LANCZOS
        
        # 2. Reescalado EXACTO a las dimensiones de la ventana (width, height)
        img = img.resize((win_w, win_h), resample_filter)
        
        # 3. Guardar archivo temporal
        img.save(self.temp_file, format="PNG")

        # 4. Destruir buffer anterior si existía
        if self.img_ptr:
            try:
                m_instance.mlx_destroy_image(mlx_ptr, self.img_ptr)
            except Exception:
                pass

        # 5. Cargar en MLX con la firma del wrapper
        res = None
        if hasattr(m_instance, 'mlx_png_file_to_image'):
            res = m_instance.mlx_png_file_to_image(mlx_ptr, self.temp_file)
        elif hasattr(m_instance, 'mlx_xpm_file_to_image'):
            res = m_instance.mlx_xpm_file_to_image(mlx_ptr, self.temp_file)
        else:
            print("[ERROR] El wrapper de MLX no ofrece métodos de carga conocidos.")
            return

        self.img_ptr = res[0] if isinstance(res, (tuple, list)) else res

    def draw(self, m_instance: Mlx, mlx_ptr, win_ptr):
        """Pinta la imagen en la posición (0,0) ocupando toda la ventana."""
        if not self.img_ptr:
            return
            
        # Posición 0, 0 exacta porque mide lo mismo que la ventana
        m_instance.mlx_put_image_to_window(mlx_ptr, win_ptr, self.img_ptr, 0, 0)

    def cleanup(self):
        """Elimina el PNG temporal."""
        if os.path.exists(self.temp_file):
            try:
                os.remove(self.temp_file)
            except OSError:
                pass


class MazeWindow:
    def __init__(self, renderer: ImageRenderer, width: int = 800, height: int = 600, title: str = "Image Stretched"):
        self.m = Mlx()
        self.mlx_ptr = self.m.mlx_init()
        self.title = title
        self.renderer = renderer
        self.win_ptr = None
        
        self.width = width
        self.height = height
        
        self._create_window(self.width, self.height)

    def _create_window(self, w: int, h: int):
        if self.win_ptr:
            self.m.mlx_destroy_window(self.mlx_ptr, self.win_ptr)
            
        self.width = w
        self.height = h
        
        self.win_ptr = self.m.mlx_new_window(self.mlx_ptr, self.width, self.height, self.title)
        
        self._setup_hooks()
        
        
        self.renderer.prepare_image(self.m, self.mlx_ptr, self.width, self.height)
        self.render_frame()

    def _setup_hooks(self):
        self.m.mlx_key_hook(self.win_ptr, self.on_key, None)
        self.m.mlx_hook(self.win_ptr, 33, 0, self.on_close, None)

    def on_key(self, keycode: int, param):
        if keycode in (65307, 53):  # ESC
            self.on_close(None)
        elif keycode in (61, 43, 65451):  # Tecla '+' para agrandar
            self._create_window(min(1920, int(self.width * 1.2)), min(1080, int(self.height * 1.2)))
        elif keycode in (45, 65453): 
            self._create_window(max(300, int(self.width * 0.8)), max(300, int(self.height * 0.8)))

    def render_frame(self):
        self.m.mlx_clear_window(self.mlx_ptr, self.win_ptr)
        self.renderer.draw(self.m, self.mlx_ptr, self.win_ptr)

    def loop_callback(self, dummy=None):
        self.render_frame()
        return 0

    def on_close(self, param):
        self.renderer.cleanup()
        self.m.mlx_loop_exit(self.mlx_ptr)

    def run(self):
        self.m.mlx_loop_hook(self.mlx_ptr, self.loop_callback, None)
        self.m.mlx_loop(self.mlx_ptr)


if __name__ == "__main__":
    image_path = "sisyphus-eternal-struggle-artwork-n1rd86b9qaqxrhtk.jpg"
    
    renderer = ImageRenderer(image_path)
    app = MazeWindow(renderer, width=800, height=800)
    
    print("Ejecutando... Usa '+' y '-' para redimensionar la ventana y la imagen al 100%.")
    app.run()