import numpy as np
from structure import MazeModel
from .Player import Player


class EngineRenderer:
    """Raycasting engine rendering pseudo-3D
    perspective with textured walls and floors."""

    def __init__(self, model: MazeModel,
                 player: Player, height: int, width: int) -> None:
        self.model = model
        self.player = player
        self.height = height
        self.width = width

        self.color_ns: int = 0xFF555555
        self.color_ew: int = 0xFF3A3A3A
        self.color_floor: int = 0xFF222222
        self.color_ceiling: int = 0xFF888888

        self.MINIMAP_SCALE: int = 8

        self.color_path: int = 0xFF55FF55
        self.color_exit: int = 0xFFFF5555

        self.path_map: np.ndarray = np.zeros((model.rows, model.cols),
                                             dtype=bool)
        self.exit_pos: tuple[int, int] = model.end

        self.tex_wall: np.ndarray | None = None
        self.tex_floor: np.ndarray | None = None
        self.tex_path: np.ndarray | None = None

    def set_textures(self, tex_wall: np.ndarray, tex_floor: np.ndarray,
                     tex_path: np.ndarray) -> None:
        self.tex_wall = tex_wall
        self.tex_floor = tex_floor
        self.tex_path = tex_path

    def update_path(self, path: list[tuple[int, int]],
                    exit_pos: tuple[int, int]) -> None:
        self.path_map = np.zeros((self.model.rows, self.model.cols),
                                 dtype=bool)
        for r, c in path:
            if 0 <= r < self.model.rows and 0 <= c < self.model.cols:
                self.path_map[r, c] = True
        self.exit_pos = exit_pos

    def put_pixel(self, screen: np.ndarray, x: int, y: int,
                  color: int) -> None:
        if 0 <= x < self.width and 0 <= y < self.height:
            screen[y, x] = color

    def draw_rect(self, screen: np.ndarray, start_x: int,
                  start_y: int, w: int, h: int, color: int) -> None:
        x0 = max(0, start_x)
        y0 = max(0, start_y)
        x1 = min(self.width, start_x + w)
        y1 = min(self.height, start_y + h)
        if x0 < x1 and y0 < y1:
            screen[y0:y1, x0:x1] = color

    def draw_line(self, screen: np.ndarray, x0: int,
                  y0: int, x1: int, y1: int, color: int) -> None:
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

        valid = ((x_vals >= 0) & (x_vals < self.width)
                 & (y_vals >= 0) & (y_vals < self.height))
        screen[y_vals[valid], x_vals[valid]] = color

    def render_minimap(self, screen: np.ndarray) -> None:
        for y in range(self.model.rows):
            for x in range(self.model.cols):
                if self.model.is_wall(x, y):
                    self.draw_rect(screen, x * self.MINIMAP_SCALE,
                                   y * self.MINIMAP_SCALE,
                                   self.MINIMAP_SCALE,
                                   self.MINIMAP_SCALE, 0xFFC8C8C8)

        exit_r, exit_c = self.exit_pos
        self.draw_rect(screen, exit_c * self.MINIMAP_SCALE,
                       exit_r * self.MINIMAP_SCALE,
                       self.MINIMAP_SCALE,
                       self.MINIMAP_SCALE,
                       self.color_exit)

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

        ray_dir_x0 = self.player.dir_x - self.player.x_plane
        ray_dir_y0 = self.player.dir_y - self.player.y_plane
        ray_dir_x1 = self.player.dir_x + self.player.x_plane
        ray_dir_y1 = self.player.dir_y + self.player.y_plane

        y_coords = np.arange(half_h, self.height)
        p = np.maximum(y_coords - half_h, 1)
        row_dist = half_h / p
        floor_step_x = row_dist * (ray_dir_x1 - ray_dir_x0) / self.width
        floor_step_y = row_dist * (ray_dir_y1 - ray_dir_y0) / self.width

        x_coords = np.arange(self.width)

        floor_x = (self.player.pos_x +
                   row_dist[:, None] *
                   ray_dir_x0 + floor_step_x[:, None] *
                   x_coords[None, :])
        floor_y = (self.player.pos_y +
                   row_dist[:, None] *
                   ray_dir_y0 + floor_step_y[:, None] * x_coords[None, :])

        grid_c = floor_x.astype(int)
        grid_r = floor_y.astype(int)

        valid = ((grid_r >= 0) &
                 (grid_r < self.model.rows) &
                 (grid_c >= 0) & (grid_c < self.model.cols))

        valid_r = grid_r[valid]
        valid_c = grid_c[valid]

        is_path = self.path_map[valid_r, valid_c]
        is_exit = (valid_r == self.exit_pos[0]) & (valid_c == self.exit_pos[1])
        is_normal_floor = ~is_path & ~is_exit

        exact_floor_x = floor_x[valid]
        exact_floor_y = floor_y[valid]

        valid_colors = np.full(valid_r.shape, self.color_floor,
                               dtype=np.uint32)

        if self.tex_floor is not None and self.tex_path is not None:
            if np.any(is_normal_floor):
                tex_h, tex_w = self.tex_floor.shape
                f_tex_x = ((exact_floor_x[is_normal_floor] *
                            tex_w).astype(int) % tex_w)
                f_tex_y = (exact_floor_y[is_normal_floor] *
                           tex_h).astype(int) % tex_h
                valid_colors[is_normal_floor] = self.tex_floor[f_tex_y,
                                                               f_tex_x]

            if np.any(is_path):
                tex_h, tex_w = self.tex_path.shape
                p_tex_x = (exact_floor_x[is_path] * tex_w).astype(int) % tex_w
                p_tex_y = (exact_floor_y[is_path] * tex_h).astype(int) % tex_h
                valid_colors[is_path] = self.tex_path[p_tex_y, p_tex_x]

        valid_colors[is_exit] = self.color_exit

        floor_colors = np.full((half_h, self.width),
                               self.color_floor, dtype=np.uint32)
        floor_colors[valid] = valid_colors
        screen[half_h:self.height, :] = floor_colors

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

                if (map_x < 0 or map_x >=
                        self.model.cols or map_y <
                        0 or map_y >= self.model.rows):
                    hit = True
                    break

                if self.model.is_wall(map_x, map_y):
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

            if self.tex_wall is not None:
                if side == 0:
                    wall_x = self.player.pos_y + perp_wall_dist * ray_dir_y
                else:
                    wall_x = self.player.pos_x + perp_wall_dist * ray_dir_x
                wall_x -= np.floor(wall_x)

                tex_wall_h, tex_wall_w = self.tex_wall.shape
                tex_x = int(wall_x * float(tex_wall_w))

                if side == 0 and ray_dir_x > 0:
                    tex_x = tex_wall_w - tex_x - 1
                if side == 1 and ray_dir_y < 0:
                    tex_x = tex_wall_w - tex_x - 1

                y_coords = np.arange(draw_start, draw_end + 1)
                d = y_coords * 256 - self.height * 128 + line_height * 128
                tex_y = ((d * tex_wall_h) / line_height) / 256
                tex_y = tex_y.astype(int)
                tex_y = np.clip(tex_y, 0, tex_wall_h - 1)

                wall_colors = self.tex_wall[tex_y, tex_x]
                if side == 1:
                    wall_colors = ((wall_colors >> 1) & 0x7F7F7F) | 0xFF0000002

                screen[draw_start:draw_end + 1, x] = wall_colors
            else:
                wall_color = self.color_ns if side == 1 else self.color_ew
                screen[draw_start:draw_end + 1, x] = wall_color

        self.render_minimap(screen)
