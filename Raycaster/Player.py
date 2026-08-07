from ..structure.MazeModel import MazeModel


class Player:
    def __init__(self, maze: MazeModel, angle: float) -> None:
        self.maze = maze
        self.pos_x = float(maze.start[0])
        self.pos_y = float(maze.start[1])

        self.angle = angle
        self.player_fov = 70

    def move(self, dx: float, dy: float) -> None:
