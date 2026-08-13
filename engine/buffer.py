import numpy as np
from structure import MazeModel
from .Player import Player


class EngineRenderer:
    def __init__(self,
                 model: MazeModel,
                 player: Player,
                 height: int,
                 width: int) -> None:
        self.model = model
        self.player = player
        self.height = height
        self.width = width

        self.color_ns: int = 0xFF555555
        self.color_ew: int = 0xFF3A3A3A
        self.color_floor: int = 0xFF222222
        self.color_ceiling: int = 0xFF888888

        self.MINIMAP_SCALE = 8

    def put_pixel(self, screen: np.ndarray,
                  x: int, y: int, color: int) -> None:
        if 0 <= x < self.width and 0 <= y < self.height:
            screen[y, x] = color

    def draw_rect(self, screen: np.ndarray, start_x: int, start_y: int,
                  w: int, h: int, color: int) -> None:
        x0 = max(0, start_x)
        y0 = max(0, start_y)
        x1 = min(self.width, start_x + w)
        y1 = min(self.height, start_y + h)
        if x0 < x1 and y0 < y1:
            screen[y0:y1, x0:x1] = color

    def draw_line(self, screen: np.ndarray, x0: int, y0: int,
                  x1: int, y1: int, color: int) -> None:
        if x0 == x1:
            y_s = max(0, min(y0, y1))
            y_e = min(self.height, max(y0, y1) + 1)
            if 0 <= x0 < self.width:
                screen[y_s:y_e, x0] = color
            return

        if y0 == y1:
            x_s = max(0, min(x0, x1))
            x_e = min(self.width, max(x0, x1) + 1)
            if 0 <= y0 < self.height:
                screen[y0, x_s:x_e] = color
            return

        length = int(np.hypot(x1 - x0, y1 - y0))
        if length == 0:
            return

        x_vals = np.linspace(x0, x1, length).astype(int)
        y_vals = np.linspace(y0, y1, length).astype(int)

        valid = (x_vals >= 0) & (x_vals < self.width) & (y_vals >= 0) & (y_vals < self.height)
        screen[y_vals[valid], x_vals[valid]] = color

    def render_minimap(self, screen: np.ndarray) -> None:
        for y in range(self.model.rows):
            for x in range(self.model.cols):
                if self.model.is_wall(y, x):
                    self.draw_rect(screen, x * self.MINIMAP_SCALE,
                                   y * self.MINIMAP_SCALE,
                                   self.MINIMAP_SCALE,
                                   self.MINIMAP_SCALE, 0xFFC8C8C8)

        cx = int(self.player.pos_x * self.MINIMAP_SCALE)
        cy = int(self.player.pos_y * self.MINIMAP_SCALE)
        ps = 4

        self.draw_rect(screen, cx - ps // 2, cy - ps // 2, ps, ps, 0xFFCC7722)

        ex = cx + int(self.player.dir_x * self.MINIMAP_SCALE)
        ey = cy + int(self.player.dir_y * self.MINIMAP_SCALE)
        self.draw_line(screen, cx, cy, ex, ey, 0xFFFFFFFF)

    def render_frame(self, screen: np.ndarray) -> None:
        half_h = self.height // 2
        screen[:half_h, :] = self.color_ceiling
        screen[half_h:, :] = self.color_floor

        for x in range(self.width):
            cam_x = 2.0 * x / float(self.width) - 1.0
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
                side_dist_y = (map_y + 1.0 - self.player.pos_y) * delta_dist_y

            while not hit:
                if side_dist_x < side_dist_y:
                    side_dist_x += delta_dist_x
                    map_x += step_x
                    side = 0
                else:
                    side_dist_y += delta_dist_y
                    map_y += step_y
                    side = 1

                if map_x < 0 or map_x >= self.model.cols or map_y < 0 or map_y >= self.model.rows:
                    hit = True
                    break
                if self.model.is_wall(map_y, map_x):
                    hit = True

            if side == 0:
                perp_wall_dist = side_dist_x - delta_dist_x
            else:
                perp_wall_dist = side_dist_y - delta_dist_y

            if perp_wall_dist <= 0:
                perp_wall_dist = 0.0001

            line_height = int(self.height / perp_wall_dist)

            draw_start = max(0, -line_height // 2 + half_h)
            draw_end = min(self.height - 1, line_height // 2 + half_h)

            wall_color = self.color_ns if side == 1 else self.color_ew

            screen[draw_start:draw_end + 1, x] = wall_color

        self.render_minimap(screen)
