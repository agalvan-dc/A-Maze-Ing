from structure.MazeModel import MazeModel
import random
import math


class Player:
    def __init__(self, maze: MazeModel) -> None:
        self.maze = maze
        if not maze.is_wall(maze.start[0], maze.start[1]):
            self.pos_x = float(maze.start[0])
            self.pos_y = float(maze.start[1])
        else:
            boo = False
            while not boo:
                i = random.randint(0, maze.rows - 1)
                j = random.randint(0, maze.cols - 1)
                if not maze.is_wall(i, j):
                    self.pos_x = float(i)
                    self.pos_y = float(j)
                    boo = True
        self.dir_x: float = 0.0
        self.dir_y: float = -1.0
        self.x_plane: float = 0.66
        self.y_plane: float = 0.0

    def move_forward(self, move_speed: float) -> None:
        new_x = self.pos_x + self.dir_x * move_speed
        new_y = self.pos_y + self.dir_y * move_speed

        if not self.maze.is_wall(int(self.pos_y), int(new_x)):
            self.pos_x = new_x
        if not self.maze.is_wall(int(new_y), int(self.pos_x)):
            self.pos_y = new_y

    def move_backward(self, move_speed: float) -> None:
        new_x = self.pos_x - self.dir_x * move_speed
        new_y = self.pos_y - self.dir_y * move_speed

        if not self.maze.is_wall(int(self.pos_y), int(new_x)):
            self.pos_x = new_x
        if not self.maze.is_wall(int(new_y), int(self.pos_x)):
            self.pos_y = new_y

    def move_left(self, move_speed: float) -> None:
        new_x = self.pos_x + self.dir_y * move_speed
        new_y = self.pos_y - self.dir_x * move_speed

        if not self.maze.is_wall(int(self.pos_y), int(new_x)):
            self.pos_x = new_x
        if not self.maze.is_wall(int(new_y), int(self.pos_x)):
            self.pos_y = new_y

    def move_right(self, move_speed: float) -> None:
        new_x = self.pos_x - self.dir_y * move_speed
        new_y = self.pos_y + self.dir_x * move_speed

        if not self.maze.is_wall(int(self.pos_y), int(new_x)):
            self.pos_x = new_x
        if not self.maze.is_wall(int(new_y), int(self.pos_x)):
            self.pos_y = new_y

    def rotate(self, angle: float) -> None:
        old_dir_x = self.dir_x
        self.dir_x = self.dir_x * math.cos(angle) - self.dir_y * math.sin(angle)
        self.dir_y = old_dir_x * math.sin(angle) + self.dir_y * math.cos(angle)

        old_plane_x = self.x_plane
        self.x_plane = self.x_plane * math.cos(angle) - self.y_plane * math.sin(angle)
        self.y_plane = old_plane_x * math.sin(angle) + self.y_plane * math.cos(angle)
