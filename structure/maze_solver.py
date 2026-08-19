from typing import Any, Protocol, TypeAlias


Coordinate: TypeAlias = tuple[int, int]
Maze: TypeAlias = dict[Coordinate, str]


class GridMaze(Protocol):
    """Protocol for maze objects exposing a physical grid."""

    grid: Any


MazeSource: TypeAlias = Maze | GridMaze


class MazeSolver:
    """Solve mazes using A* on logical maze coordinates."""

    def __init__(
        self,
        maze: MazeSource,
        entry: Coordinate,
        exit: Coordinate,
    ) -> None:
        """Initialize the maze solver.

        Args:
            maze: Maze data represented either as a coordinate dictionary
                or as an object exposing a physical grid.
            entry: Logical coordinate of the maze entry.
            exit: Logical coordinate of the maze exit.
        """
        self.maze = maze
        self.entry = entry
        self.exit = exit

        self.wall = "█"
        self.forty_two = "\033[38;5;208m█\033[0m"

        if hasattr(maze, "grid"):
            physical_height, physical_width = maze.grid.shape
        else:
            physical_width = max(
                x for x, y in maze
            ) + 1
            physical_height = max(
                y for x, y in maze
            ) + 1

        self.width = (physical_width - 1) // 2
        self.height = (physical_height - 1) // 2

        self.path: list[Coordinate] = []
        self.visited: list[Coordinate] = []

        self.a_star()

    def get_cell(self, x: int, y: int) -> Any:
        """Return the cell value at a physical coordinate.

        Args:
            x: Physical x-coordinate of the cell.
            y: Physical y-coordinate of the cell.

        Returns:
            The value stored at the requested cell, or a wall value when
            the coordinate is outside the maze boundaries.
        """
        if hasattr(self.maze, "grid"):
            grid = self.maze.grid

            if not (
                0 <= y < grid.shape[0]
                and 0 <= x < grid.shape[1]
            ):
                return self.wall

            return grid[y, x]

        return self.maze.get((x, y), self.wall)

    def is_wall(self, x: int, y: int) -> bool:
        """Determine whether a physical cell is blocked.

        Args:
            x: Physical x-coordinate of the cell.
            y: Physical y-coordinate of the cell.

        Returns:
            True when the cell contains a wall or the 42 marker.
        """
        cell = self.get_cell(x, y)

        if cell == 1:
            return True

        if cell == 2:
            return True

        if cell == self.wall:
            return True

        if cell == self.forty_two:
            return True

        return False

    def can_move(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
    ) -> bool:
        """Check whether movement between two logical cells is possible.

        Logical coordinates are converted to physical coordinates so that
        both the destination cell and the intermediate wall can be checked.

        Args:
            x1: Logical x-coordinate of the source cell.
            y1: Logical y-coordinate of the source cell.
            x2: Logical x-coordinate of the destination cell.
            y2: Logical y-coordinate of the destination cell.

        Returns:
            True when the destination and intermediate cell are traversable.
        """
        if not (
            0 <= x2 < self.width
            and 0 <= y2 < self.height
        ):
            return False

        px1 = x1 * 2 + 1
        py1 = y1 * 2 + 1

        px2 = x2 * 2 + 1
        py2 = y2 * 2 + 1

        if self.is_wall(px2, py2):
            return False

        mx = (px1 + px2) // 2
        my = (py1 + py2) // 2

        if self.is_wall(mx, my):
            return False

        return True

    def get_path(self) -> list[Coordinate]:
        """Return the calculated logical path.

        Returns:
            The logical coordinates forming the path from entry to exit.
        """
        return self.path

    def get_visited(self) -> list[Coordinate]:
        """Return the logical cells visited by the A* algorithm.

        Returns:
            The logical coordinates visited while searching for the exit.
        """
        return self.visited

    @staticmethod
    def heuristic(
        a: Coordinate,
        b: Coordinate,
    ) -> int:
        """Calculate the Manhattan distance between two coordinates.

        Args:
            a: First logical coordinate.
            b: Second logical coordinate.

        Returns:
            The Manhattan distance between the two coordinates.
        """
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def a_star(self) -> list[Coordinate]:
        """Find a path between the entry and exit using A*.

        The algorithm operates exclusively on logical maze coordinates.
        Physical coordinates are only used when checking maze cells.

        Returns:
            The logical coordinates forming the path, or an empty list when
            no valid path exists.
        """
        if not (
            0 <= self.entry[0] < self.width
            and 0 <= self.entry[1] < self.height
        ):
            self.path = []
            return []

        if not (
            0 <= self.exit[0] < self.width
            and 0 <= self.exit[1] < self.height
        ):
            self.path = []
            return []

        open_list: list[Coordinate] = [self.entry]

        visited_set: set[Coordinate] = set()

        g_score: dict[Coordinate, int] = {
            self.entry: 0
        }

        f_score: dict[Coordinate, int] = {
            self.entry: self.heuristic(
                self.entry,
                self.exit,
            )
        }

        came_from: dict[Coordinate, Coordinate] = {}

        while open_list:
            current = min(
                open_list,
                key=lambda node: f_score.get(
                    node,
                    float("inf"),
                ),
            )

            if current == self.exit:
                path: list[Coordinate] = []

                while current in came_from:
                    path.append(current)
                    current = came_from[current]

                path.append(self.entry)

                self.path = path[::-1]
                return self.path

            open_list.remove(current)
            visited_set.add(current)

            self.visited.append(current)

            x, y = current

            neighbors: list[Coordinate] = [
                (x + 1, y),
                (x - 1, y),
                (x, y + 1),
                (x, y - 1),
            ]

            for neighbor in neighbors:
                nx, ny = neighbor

                if not (
                    0 <= nx < self.width
                    and 0 <= ny < self.height
                ):
                    continue

                if neighbor in visited_set:
                    continue

                if not self.can_move(
                    x,
                    y,
                    nx,
                    ny,
                ):
                    continue

                tentative_g_score = g_score[current] + 1

                if (
                    neighbor not in g_score
                    or tentative_g_score < g_score[neighbor]
                ):
                    came_from[neighbor] = current

                    g_score[neighbor] = tentative_g_score

                    f_score[neighbor] = (
                        tentative_g_score
                        + self.heuristic(
                            neighbor,
                            self.exit,
                        )
                    )

                    if neighbor not in open_list:
                        open_list.append(neighbor)

        self.path = []
        return []

    def get_cell_hex(self, x: int, y: int) -> str:
        """Convert a logical cell to its hexadecimal wall representation.

        Logical coordinates are converted to physical coordinates before
        inspecting the surrounding walls.

        Args:
            x: Logical x-coordinate.
            y: Logical y-coordinate.

        Returns:
            A hexadecimal representation of the cell's surrounding walls.

        Raises:
            ValueError: If the logical coordinate is outside the maze.
        """
        if not (
            0 <= x < self.width
            and 0 <= y < self.height
        ):
            raise ValueError(
                f"Logical coordinate out of bounds: {(x, y)}"
            )

        physical_x = x * 2 + 1
        physical_y = y * 2 + 1

        cell = self.get_cell(
            physical_x,
            physical_y,
        )

        if cell == self.forty_two:
            return "F"

        walls = 0

        if self.is_wall(
            physical_x,
            physical_y - 1,
        ):
            walls |= 1

        if self.is_wall(
            physical_x + 1,
            physical_y,
        ):
            walls |= 2

        if self.is_wall(
            physical_x,
            physical_y + 1,
        ):
            walls |= 4

        if self.is_wall(
            physical_x - 1,
            physical_y,
        ):
            walls |= 8

        return format(walls, "X")

    def path_to_directions(self) -> str:
        """Convert the logical path into movement directions.

        Each consecutive pair of logical cells is converted into one
        cardinal direction.

        Returns:
            A string containing the path directions using N, S, E and W.
        """
        directions: list[str] = []

        for i in range(1, len(self.path)):
            current = self.path[i - 1]
            next_cell = self.path[i]

            dx = next_cell[0] - current[0]
            dy = next_cell[1] - current[1]

            if dx == 1:
                directions.append("E")
            elif dx == -1:
                directions.append("W")
            elif dy == 1:
                directions.append("S")
            elif dy == -1:
                directions.append("N")

        return "".join(directions)

    def write_output(self, filename: str) -> None:
        """Write the logical maze and solution to an output file.

        The maze cells, entry, exit and path are written using logical
        coordinates.

        Args:
            filename: Path of the output file to create.
        """
        with open(filename, "w", encoding="utf-8") as file:
            for y in range(self.height):
                line = ""

                for x in range(self.width):
                    line += self.get_cell_hex(x, y)

                file.write(line + "\n")

            file.write("\n")

            if self.get_cell_hex(self.entry) != 'F':
                file.write(
                    f"{self.entry[0]},{self.entry[1]}\n"
                )
            else:
                print("Entry detected in 42 square. Placing in 0,0...")
                file.write(f"{0,0}")

            file.write(
                f"{self.exit[0]},{self.exit[1]}\n"
            )

            file.write(
                self.path_to_directions() + "\n"
            )
