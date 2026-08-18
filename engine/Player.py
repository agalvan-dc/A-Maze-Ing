from structure.maze_model import MazeModel
import random
import math


class Player:
    """Manages player position, camera direction vectors,
    collision detection, and rotation.

    Attributes:
        maze: MazeModel instance used for collision checks.
        pos_x: Horizontal coordinate in map grid units.
        pos_y: Vertical coordinate in map grid units.
        dir_x: Horizontal component of the direction vector.
        dir_y: Vertical component of the direction vector.
        x_plane: Horizontal component of the camera FOV plane vector.
        y_plane: Vertical component of the camera FOV plane vector.
    """

    def __init__(self, maze: MazeModel) -> None:
        """Initializes player spawn coordinates, camera orientation,
        and FOV plane vectors.

        Args:
            maze: The maze layout model providing wall
            boundaries and start position.
        """
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
        self.margin = 0.2

    def move_forward(self, move_speed: float) -> None:
        """Translates the player forward along the directional
        vector with collision handling.

        Args:
            move_speed: Distance step multiplier applied to
            movement calculations.
        """
        new_x = self.pos_x + self.dir_x * move_speed
        new_y = self.pos_y + self.dir_y * move_speed

        check_x = (new_x + self.margin if self.dir_x >
                   0 else new_x - self.margin)
        check_y = (new_y + self.margin if self.dir_y >
                   0 else new_y - self.margin)

        if not self.maze.is_wall(int(check_x), int(self.pos_y)):
            self.pos_x = new_x
        if not self.maze.is_wall(int(self.pos_x), int(check_y)):
            self.pos_y = new_y

    def move_backward(self, move_speed: float) -> None:
        """Translates the player backward against the directional
        vector with collision handling.

        Args:
            move_speed: Distance step multiplier applied to
            movement calculations.
        """
        new_x = self.pos_x - self.dir_x * move_speed
        new_y = self.pos_y - self.dir_y * move_speed

        check_x = (new_x + self.margin if self.dir_x >
                   0 else new_x - self.margin)
        check_y = (new_y + self.margin if self.dir_y >
                   0 else new_y - self.margin)

        if not self.maze.is_wall(int(check_x), int(self.pos_y)):
            self.pos_x = new_x
        if not self.maze.is_wall(int(self.pos_x), int(check_y)):
            self.pos_y = new_y

    def move_left(self, move_speed: float) -> None:
        """Strafes the player to the left relative to the current
        direction vector.

        Args:
            move_speed: Distance step multiplier applied to
            movement calculations.
        """
        new_x = self.pos_x + self.dir_y * move_speed
        new_y = self.pos_y - self.dir_x * move_speed

        check_x = (new_x + self.margin if self.dir_x >
                   0 else new_x - self.margin)
        check_y = (new_y + self.margin if self.dir_y >
                   0 else new_y - self.margin)

        if not self.maze.is_wall(int(check_x), int(self.pos_y)):
            self.pos_x = new_x
        if not self.maze.is_wall(int(self.pos_x), int(check_y)):
            self.pos_y = new_y

    def move_right(self, move_speed: float) -> None:
        """Strafes the player to the right relative to the
        current direction vector.

        Args:
            move_speed: Distance step multiplier applied to
            movement calculations.
        """
        new_x = self.pos_x - self.dir_y * move_speed
        new_y = self.pos_y + self.dir_x * move_speed

        check_x = (new_x + self.margin if self.dir_x >
                   0 else new_x - self.margin)
        check_y = (new_y + self.margin if self.dir_y >
                   0 else new_y - self.margin)

        if not self.maze.is_wall(int(check_x), int(self.pos_y)):
            self.pos_x = new_x
        if not self.maze.is_wall(int(self.pos_x), int(check_y)):
            self.pos_y = new_y

    def rotate(self, angle: float) -> None:
        """Rotates direction and camera projection plane
        vectors using a 2D matrix transform.

        Args:
            angle: Rotation magnitude in radians.
        """
        old_dir_x = self.dir_x
        self.dir_x = (self.dir_x * math.cos(angle) -
                      self.dir_y * math.sin(angle))
        self.dir_y = old_dir_x * math.sin(angle) + self.dir_y * math.cos(angle)

        old_plane_x = self.x_plane
        self.x_plane = (self.x_plane * math.cos(angle) -
                        self.y_plane * math.sin(angle))
        self.y_plane = (old_plane_x * math.sin(angle) +
                        self.y_plane * math.cos(angle))
