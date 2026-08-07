import math
import sys
import ctypes
from ..structure import MazeModel
from .Player import Player

class EngineRenderer:
    def __init__(self,
                 model: MazeModel,
                 player: Player) -> None:
        self.model = model
        self.player = player

        self.color_ns: int = 0x555555
        self.color_ew: int = 0x3A3A3A
        self.color_floor: int = 0x222222
        self.color_ceiling: int = 0x888888

        self.MINIMAP_SCALE = 10

    def put_pixel(self,
                  buffer, width: int,
                  x: int, y: int, color: int,
                  max_height: int) -> None:
        if 0 <= x < width and 0 <= y < max_height:
            buffer[y * width + x] = color

    def draw_rect(self, buffer, width: int,
                  start_x: int, start_y: int,
                  w: int, h: int, color: int, max_h: int) -> None:
        for y in range(start_y, start_y + h):
            for x in range(start_x, start_x + w):
                self.put_pixel(buffer, width, x, y, color, max_h)

    def draw_line(self, buffer, width: int,
                  x0: int, y0: int, x1: int,
                  y1: int, color: int, max_h: int) -> None:
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy

        while True:
            self.put_pixel(buffer, width, x0, y0, color, max_h)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def render_minimap(self, buffer, width: int, height: int) -> None:
        for y in range(self.model.rows):
            for x in range(self.model.cols):
                if self.model.is_wall(y, x):
                    self.draw_rect(buffer, width, x * self.MINIMAP_SCALE,
                                   y * self.MINIMAP_SCALE, 
                                   self.MINIMAP_SCALE,
                                   self.MINIMAP_SCALE, 0xC8C8C8, height)

        center_x = int(self.player.pos_x * self.MINIMAP_SCALE)
        center_y = int(self.player.pos_y * self.MINIMAP_SCALE)
        
        p_size = 4
        self.draw_rect(buffer, width, center_x - p_size//2,
                       center_y - p_size//2, 
                       p_size, p_size, 0xCC7722, height)

        end_x = center_x + int(self.player.dir_x * self.MINIMAP_SCALE)
        end_y = center_y + int(self.player.dir_y * self.MINIMAP_SCALE)
        self.draw_line(buffer, width, center_x, center_y, end_x, end_y, 0xFFFFFF, height)

    def render_frame(self, window) -> None:
        width = window.width
        height = window.height

        data_info = window.m.mlx_get_data_addr(window.imp_ptr)
        try:
            buffer_ptr = ctypes.cast(data_info[0], ctypes.POINTER(ctypes.c_uint32 * (width * height)))
            pixel_buffer = buffer_ptr.contents
        except TypeError:
            print("Buffer not compatible with ctypes")
            sys.exit(1)

        for y in range(height // 2):
            for x in range(width):
                pixel_buffer[y * width + x] = self.color_ceiling
        for y in range(height // 2, height):
            for x in range(width):
                pixel_buffer[y * width + x] = self.color_floor

        for x in range(width):
            cam_x = 2.0 * x / float(width) - 1.0
            ray_dir_x = self.player.dir_x + self.player.x_plane * cam_x
            ray_dir_y = self.player.dir_y + self.player.y_plane * cam_x

            map_x = int(self.player.pos_x)
            map_y = int(self.player.pos_y)

            delta_dist_x = 1e30 if ray_dir_x == 0 else abs(1.0 / ray_dir_x)
            delta_dist_y = 1e30 if ray_dir_y == 0 else abs(1.0 / ray_dir_y)

            hit = False
            side = 0

            if ray_dir_x < 0:
                step_x = -1
                side_dist_x = (self.player.pos_x - map_x) * delta_dist_x
            else:
                step_x = 1
                side_dist_x = (map_x + 1.0 - self.player.pos_x) * delta_dist_x
            if ray_dir_y < 0:
                step_y = -1
                side_dist_y = (self.player.pos_y - map_y) * delta_dist_y
            else:
                step_y = 1
                side_dist_y = (map_x + 1.0 - self.player.pos_y) * delta_dist_y
            # ft_perform_dda
            while not hit:
                if side_dist_x < side_dist_y:
                    side_dist_x += delta_dist_x
                    map_x += step_x
                    side = 0
                else:
                    side_dist_y += side_dist_y
                    map_y += step_y
                    side = 1

                if map_x < 0 or map_x >= self.model.cols or map_y < 0 or map_y >= self.model.rows:
                    hit = True
                    break
                if self.model.is_wall(map_y, map_x):
                    hit = True
            # ft_calculate_line
            if side == 0:
                perp_wall_dist = side_dist_x - delta_dist_x
            else:
                perp_wall_dist = side_dist_y - delta_dist_y

            if perp_wall_dist <= 0:
                perp_wall_dist = 0.0001
            
            line_height = int(height / perp_wall_dist)

            draw_start = -line_height // 2 + height // 2
            if draw_start < 0:
                draw_start = 0

            draw_end = line_height // 2 + height // 2
            if draw_end >= height:
                draw_end = height - 1

            wall_color = self.color_ns if side == 1 else self.color_ew

            for y in range(draw_start, draw_end + 1):
                pixel_buffer[y * width + x] = wall_color

        self.render_minimap(pixel_buffer, width, height)
