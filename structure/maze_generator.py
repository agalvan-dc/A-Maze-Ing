import os
import random
from typing import Any, TypeAlias
from .parsing import validate_conf


Coordinate: TypeAlias = tuple[int, int]
Maze: TypeAlias = dict[Coordinate, str]
Config: TypeAlias = dict[str, Any]


class MazeGenerator:
    """Generate and display maze structures."""

    def __init__(self, config_path: str = "./utilities/config.txt") -> None:
        """Initialize the maze generator.

        Args:
            config_path: Path to the maze configuration file.
        """
        self.EMPTY = " "
        self.MARK = "@"
        self.WALL = chr(9608)
        self.NORTH, self.SOUTH, self.EAST, self.WEST = "n", "s", "e", "w"
        self.BLUE = "\033[44m \033[0m"
        self.RED = "\033[41m \033[0m"
        self.FORTY_TWO = "\033[38;5;208m█\033[0m"
        self.config_path = os.path.expanduser(config_path)
        self.warning_msg: str | None = None

    def get_config(self) -> Config:
        """Load and validate the maze configuration.

        Returns:
            A validated maze configuration dictionary.
        """
        return validate_conf(self.config_path)

    def put_ft_in_maze(
        self,
        maze: Maze,
        width: int,
        height: int,
    ) -> None:
        """Place the '42' pattern inside the maze.

        Args:
            maze: Maze grid represented as coordinate-keyed cells.
            width: Physical width of the maze.
            height: Physical height of the maze.
        """
        logical_width = (width - 1) // 2
        logical_height = (height - 1) // 2

        if logical_width < 9 or logical_height < 9:
            return

        width_center = logical_width // 2
        height_center = logical_height // 2

        forty_two = [
            (-1, 0),
            (-2, 0),
            (-3, 0),
            (-3, -1),
            (-3, -2),
            (-1, 1),
            (-1, 2),
            (1, 0),
            (2, 0),
            (3, 0),
            (1, 1),
            (1, 2),
            (2, 2),
            (3, 2),
            (1, -2),
            (2, -2),
            (3, -2),
            (3, -1),
        ]

        empty = [
            (0, 0),
            (0, 1),
            (0, 2),
            (2, 1),
            (2, -1),
            (-2, -1),
            (-2, -2),
            (-2, 1),
            (-2, 2),
            (-1, -1),
            (1, -1),
            (3, 1),
        ]

        for dx, dy in forty_two:
            x = width_center + dx
            y = height_center + dy

            physical_x = x * 2 + 1
            physical_y = y * 2 + 1

            if (
                0 <= physical_x < width
                and 0 <= physical_y < height
            ):
                maze[(physical_x, physical_y)] = self.FORTY_TWO

        for dx, dy in empty:
            x = width_center + dx
            y = height_center + dy

            physical_x = x * 2 + 1
            physical_y = y * 2 + 1

            if (
                0 <= physical_x < width
                and 0 <= physical_y < height
            ):
                maze[(physical_x, physical_y)] = self.EMPTY

    def do_basic(
        self,
        dict_data: Config,
        maze: Maze,
    ) -> Maze:
        """Generate a maze using the basic generation algorithm.

        Args:
            dict_data: Maze generation configuration.
            maze: Initially initialized maze grid.

        Returns:
            The generated maze.
        """
        width = int(dict_data["width"]) * 2 + 1
        height = int(dict_data["height"]) * 2 + 1

        logical_entry = dict_data["entry"]
        entry = (
            logical_entry[0] * 2 + 1,
            logical_entry[1] * 2 + 1,
        )

        logical_exit = dict_data["exit"]
        exit_pos = (
            logical_exit[0] * 2 + 1,
            logical_exit[1] * 2 + 1,
        )

        perfect = dict_data["perfect"]
        seed = dict_data["seed"]

        if seed and seed != "" and seed != "random" and seed != "RANDOM":
            random.seed(seed)
        else:
            random.seed()

        if exit_pos > (width, height) or exit_pos < (0, 0):
            raise Exception(
                "exit coords invalid, please put a number between "
                "width and height"
            )
        elif entry > (width, height) or entry < (0, 0):
            raise Exception(
                "entry coords invalid, please put a number between "
                "width and height"
            )

        if width > 9 and height > 9:
            self.put_ft_in_maze(maze, width, height)

        if width <= 9 or height <= 9:
            self.warning_msg = "Can't put 42 in maze"

        has_visited: list[Coordinate] = []

        def visit(x: int, y: int) -> None:
            """Visit maze cells recursively during generation.

            Args:
                x: Physical x-coordinate of the current cell.
                y: Physical y-coordinate of the current cell.
            """
            next_x = 0
            next_y = 0

            if maze.get((x, y)) != self.FORTY_TWO:
                maze[(x, y)] = self.EMPTY

            while True:
                unvisited_neighbors: list[str] = []

                if (
                    y - 2 >= 1
                    and (x, y - 2) not in has_visited
                    and maze.get((x, y - 2)) != self.FORTY_TWO
                    and maze.get((x, y - 1)) != self.FORTY_TWO
                ):
                    unvisited_neighbors.append(self.NORTH)

                if (
                    y + 2 < height - 1
                    and (x, y + 2) not in has_visited
                    and maze.get((x, y + 2)) != self.FORTY_TWO
                    and maze.get((x, y + 1)) != self.FORTY_TWO
                ):
                    unvisited_neighbors.append(self.SOUTH)

                if (
                    x - 2 >= 1
                    and (x - 2, y) not in has_visited
                    and maze.get((x - 2, y)) != self.FORTY_TWO
                    and maze.get((x - 1, y)) != self.FORTY_TWO
                ):
                    unvisited_neighbors.append(self.WEST)

                if (
                    x + 2 < width - 1
                    and (x + 2, y) not in has_visited
                    and maze.get((x + 2, y)) != self.FORTY_TWO
                    and maze.get((x + 1, y)) != self.FORTY_TWO
                ):
                    unvisited_neighbors.append(self.EAST)

                if len(unvisited_neighbors) == 0:
                    return

                next_tile = random.choice(unvisited_neighbors)

                if next_tile == self.NORTH:
                    next_x, next_y = x, y - 2
                    maze[(x, y - 1)] = self.EMPTY
                elif next_tile == self.SOUTH:
                    next_x, next_y = x, y + 2
                    maze[(x, y + 1)] = self.EMPTY
                elif next_tile == self.WEST:
                    next_x, next_y = x - 2, y
                    maze[(x - 1, y)] = self.EMPTY
                elif next_tile == self.EAST:
                    next_x, next_y = x + 2, y
                    maze[(x + 1, y)] = self.EMPTY

                has_visited.append((next_x, next_y))
                visit(next_x, next_y)

        has_visited = [entry]
        visit(1, 1)

        if perfect == "False" or perfect is False:
            for y in range(1, height - 1, 2):
                for x in range(1, width - 1, 2):
                    if maze[(x, y)] != self.EMPTY:
                        continue

                    wall_neighbors: list[str] = []

                    if maze.get((x, y - 1)) in (
                        self.WALL,
                        self.FORTY_TWO,
                    ):
                        wall_neighbors.append(self.NORTH)

                    if maze.get((x, y + 1)) in (
                        self.WALL,
                        self.FORTY_TWO,
                    ):
                        wall_neighbors.append(self.SOUTH)

                    if maze.get((x - 1, y)) in (
                        self.WALL,
                        self.FORTY_TWO,
                    ):
                        wall_neighbors.append(self.WEST)

                    if maze.get((x + 1, y)) in (
                        self.WALL,
                        self.FORTY_TWO,
                    ):
                        wall_neighbors.append(self.EAST)

                    if len(wall_neighbors) == 3:
                        secure_options: list[str] = []

                        if (
                            self.NORTH in wall_neighbors
                            and y > 1
                            and maze.get((x, y - 1)) == self.WALL
                            and maze.get((x, y - 2)) != self.FORTY_TWO
                        ):
                            secure_options.append(self.NORTH)

                        if (
                            self.SOUTH in wall_neighbors
                            and y < height - 2
                            and maze.get((x, y + 1)) == self.WALL
                            and maze.get((x, y + 2)) != self.FORTY_TWO
                        ):
                            secure_options.append(self.SOUTH)

                        if (
                            self.WEST in wall_neighbors
                            and x > 1
                            and maze.get((x - 1, y)) == self.WALL
                            and maze.get((x - 2, y)) != self.FORTY_TWO
                        ):
                            secure_options.append(self.WEST)

                        if (
                            self.EAST in wall_neighbors
                            and x < width - 2
                            and maze.get((x + 1, y)) == self.WALL
                            and maze.get((x + 2, y)) != self.FORTY_TWO
                        ):
                            secure_options.append(self.EAST)

                        if secure_options:
                            wall_to_break = random.choice(
                                secure_options
                            )

                            if wall_to_break == self.NORTH:
                                maze[(x, y - 1)] = self.EMPTY
                            elif wall_to_break == self.SOUTH:
                                maze[(x, y + 1)] = self.EMPTY
                            elif wall_to_break == self.WEST:
                                maze[(x - 1, y)] = self.EMPTY
                            elif wall_to_break == self.EAST:
                                maze[(x + 1, y)] = self.EMPTY

        maze[entry] = self.BLUE
        maze[exit_pos] = self.RED

        return maze

    def generate_maze(
        self,
        input_dict: Config,
        algo: str = "basic",
    ) -> Maze:
        """Generate a maze using the selected algorithm.

        Args:
            input_dict: Maze generation configuration.
            algo: Name of the generation algorithm to use.

        Returns:
            The generated maze.
        """
        width = int(input_dict["width"]) * 2 + 1
        height = int(input_dict["height"]) * 2 + 1

        maze: Maze = {}

        for y in range(height):
            for x in range(width):
                maze[(x, y)] = self.WALL

        if algo == "basic":
            maze = self.do_basic(input_dict, maze)
        elif algo == "prueba":
            exit()
        else:
            exit()

        return maze

    def print_maze(self, maze: Maze) -> None:
        """Print the generated maze to standard output.

        Args:
            maze: Maze grid represented as coordinate-keyed cells.
        """
        width = max(coordinate[0] for coordinate in maze) + 1
        height = max(coordinate[1] for coordinate in maze) + 1

        for y in range(height):
            for x in range(width):
                print(maze[x, y], end="")
            print()

        if self.warning_msg:
            print(self.warning_msg)
