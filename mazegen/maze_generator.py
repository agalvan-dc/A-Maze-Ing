from __future__ import annotations

from collections import deque
import random
from typing import TypeAlias


Coordinate: TypeAlias = tuple[int, int]
Maze: TypeAlias = dict[Coordinate, str]


class MazeGenerator:
    """Reusable maze generator.

    The generator creates a maze using a randomized depth-first search
    algorithm. It can optionally add loops when ``perfect`` is False.

    Example:
        generator = MazeGenerator(width=20, height=20, seed=42)
        maze = generator.generate()
        solution = generator.solve()

    The generated maze is available through ``generator.maze`` and the
    solution through ``generator.solution``.
    """

    EMPTY = " "
    WALL = chr(9608)
    BLUE = "\033[44m \033[0m"
    RED = "\033[41m \033[0m"
    FORTY_TWO = "\033[38;5;208m█\033[0m"

    NORTH = "n"
    SOUTH = "s"
    EAST = "e"
    WEST = "w"

    def __init__(
        self,
        width: int,
        height: int,
        seed: int | str | None = None,
        entry: Coordinate = (0, 0),
        exit: Coordinate | None = None,
        perfect: bool = True,
    ) -> None:
        """Create a maze generator.

        Args:
            width: Maze width in logical cells.
            height: Maze height in logical cells.
            seed: Optional seed used for deterministic generation.
                  If seed is 0, it will generate a completely random maze.
            entry: Entry position in logical coordinates.
            exit: Exit position in logical coordinates. If omitted,
                the bottom-right cell is used.
            perfect: If True, generate a perfect maze. If False,
                additional walls may be removed to create loops.

        Raises:
            ValueError: If dimensions or coordinates are invalid.
        """
        if width < 1 or height < 1:
            raise ValueError("width and height must be positive")

        # Si seed es 0, lo pasamos a None para que randomice completamente
        if seed == 0:
            seed = None

        self.width = width
        self.height = height
        self.seed = seed
        self.entry = entry
        self.exit = exit if exit is not None else (width - 1, height - 1)
        self.perfect = perfect

        self.physical_width = width * 2 + 1
        self.physical_height = height * 2 + 1

        self.maze: Maze = {}
        self.solution: list[Coordinate] = []

        self.warning_msg: str | None = None

        self._validate_coordinates()

        # Keep the random generator local to this instance.
        # This avoids changing Python's global random state.
        self._random = random.Random(seed)

    def _validate_coordinates(self) -> None:
        """Validate entry and exit logical coordinates."""
        for name, coordinate in (
            ("entry", self.entry),
            ("exit", self.exit),
        ):
            if len(coordinate) != 2:
                raise ValueError(
                    f"{name} must contain exactly two coordinates"
                )

            x, y = coordinate

            if not (0 <= x < self.width and 0 <= y < self.height):
                raise ValueError(
                    f"{name} coordinates {coordinate} are outside "
                    f"the maze"
                )

    def _logical_to_physical(
        self,
        coordinate: Coordinate,
    ) -> Coordinate:
        """Convert logical coordinates to physical maze coordinates."""
        x, y = coordinate
        return x * 2 + 1, y * 2 + 1

    def _initialize_maze(self) -> None:
        """Initialize the physical maze entirely with walls."""
        self.maze = {
            (x, y): self.WALL
            for y in range(self.physical_height)
            for x in range(self.physical_width)
        }

    def _add_forty_two(self) -> None:
        """Place the 42 pattern in the center of sufficiently large mazes."""
        if self.width < 9 or self.height < 9:
            self.warning_msg = "Can't put 42 in maze"
            return

        center_x = self.width // 2
        center_y = self.height // 2

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
            logical_x = center_x + dx
            logical_y = center_y + dy
            physical = self._logical_to_physical(
                (logical_x, logical_y)
            )

            if self._inside_physical(physical):
                self.maze[physical] = self.FORTY_TWO

        for dx, dy in empty:
            logical_x = center_x + dx
            logical_y = center_y + dy
            physical = self._logical_to_physical(
                (logical_x, logical_y)
            )

            if self._inside_physical(physical):
                self.maze[physical] = self.EMPTY

    def _inside_physical(self, coordinate: Coordinate) -> bool:
        """Return whether a physical coordinate is inside the maze."""
        x, y = coordinate

        return (
            0 <= x < self.physical_width
            and 0 <= y < self.physical_height
        )

    def _neighbors(
        self,
        coordinate: Coordinate,
        visited: set[Coordinate],
    ) -> list[tuple[str, Coordinate]]:
        """Return unvisited neighboring logical cells."""
        x, y = coordinate

        candidates = [
            (self.NORTH, (x, y - 1)),
            (self.SOUTH, (x, y + 1)),
            (self.WEST, (x - 1, y)),
            (self.EAST, (x + 1, y)),
        ]

        return [
            (direction, neighbor)
            for direction, neighbor in candidates
            if (
                0 <= neighbor[0] < self.width
                and 0 <= neighbor[1] < self.height
                and neighbor not in visited
                and self._logical_cell_is_available(neighbor)
            )
        ]

    def _logical_cell_is_available(
        self,
        coordinate: Coordinate,
    ) -> bool:
        """Return whether a logical cell can be used by generation."""
        physical = self._logical_to_physical(coordinate)
        return self.maze.get(physical) != self.FORTY_TWO

    def _remove_wall(
        self,
        first: Coordinate,
        second: Coordinate,
    ) -> None:
        """Remove the physical wall between two logical cells."""
        first_x, first_y = self._logical_to_physical(first)
        second_x, second_y = self._logical_to_physical(second)

        wall = (
            (first_x + second_x) // 2,
            (first_y + second_y) // 2,
        )

        self.maze[first_x, first_y] = self.EMPTY
        self.maze[second_x, second_y] = self.EMPTY
        self.maze[wall] = self.EMPTY

    def _generate_basic(self) -> None:
        """Generate a maze using recursive randomized DFS."""
        start = self.entry
        visited: set[Coordinate] = {start}

        start_physical = self._logical_to_physical(start)

        if self.maze[start_physical] != self.FORTY_TWO:
            self.maze[start_physical] = self.EMPTY

        def dfs(current: Coordinate) -> None:
            neighbors = self._neighbors(current, visited)

            if not neighbors:
                return

            _, next_cell = self._random.choice(neighbors)

            self._remove_wall(current, next_cell)
            visited.add(next_cell)

            dfs(next_cell)

            dfs(current)

        dfs(start)

    def _create_loops(self) -> None:
        """Remove dead ends by opening valid walls."""

        changed = True

        while changed:
            changed = False

            for y in range(self.height):
                for x in range(self.width):
                    current = (x, y)
                    physical = self._logical_to_physical(current)

                    if self.maze.get(physical) not in (
                        self.EMPTY,
                        self.BLUE,
                        self.RED,
                    ):
                        continue

                    neighbors: list[tuple[str, Coordinate, Coordinate]] = []

                    if y > 0:
                        neighbors.append((
                            self.NORTH,
                            (x, y - 1),
                            (physical[0], physical[1] - 1),
                        ))

                    if y < self.height - 1:
                        neighbors.append((
                            self.SOUTH,
                            (x, y + 1),
                            (physical[0], physical[1] + 1),
                        ))

                    if x > 0:
                        neighbors.append((
                            self.WEST,
                            (x - 1, y),
                            (physical[0] - 1, physical[1]),
                        ))

                    if x < self.width - 1:
                        neighbors.append((
                            self.EAST,
                            (x + 1, y),
                            (physical[0] + 1, physical[1]),
                        ))

                    open_neighbors = [
                        neighbor
                        for _, neighbor, wall in neighbors
                        if self.maze.get(wall) == self.EMPTY
                    ]

                    if len(open_neighbors) > 1:
                        continue

                    candidates = [
                        (direction, neighbor, wall)
                        for direction, neighbor, wall in neighbors
                        if (
                            self.maze.get(wall) == self.WALL
                            and self.maze.get(
                                self._logical_to_physical(neighbor)
                            ) != self.FORTY_TWO
                        )
                    ]

                    if not candidates:
                        continue

                    _, neighbor, wall = self._random.choice(candidates)

                    self.maze[wall] = self.EMPTY

                    changed = True

    def generate(self) -> Maze:
        """Generate and return the maze structure.

        Returns:
            A dictionary mapping physical ``(x, y)`` coordinates
            to their corresponding cell character.
        """
        self._initialize_maze()
        self.warning_msg = None

        self._add_forty_two()
        self._generate_basic()

        if not self.perfect:
            self._create_loops()

        entry_physical = self._logical_to_physical(self.entry)
        exit_physical = self._logical_to_physical(self.exit)

        self.maze[entry_physical] = self.BLUE
        self.maze[exit_physical] = self.RED

        self.solve()

        return self.maze

    def solve(self) -> list[Coordinate]:
        """Find a shortest solution from entry to exit.

        Returns:
            A list of physical ``(x, y)`` coordinates forming the
            solution path. The list is empty if no solution exists.

        Raises:
            RuntimeError: If the maze has not been generated yet.
        """
        if not self.maze:
            raise RuntimeError(
                "Generate the maze before requesting its solution"
            )

        start = self._logical_to_physical(self.entry)
        target = self._logical_to_physical(self.exit)

        queue: deque[Coordinate] = deque([start])
        previous: dict[Coordinate, Coordinate | None] = {
            start: None
        }

        passable = {
            self.EMPTY,
            self.BLUE,
            self.RED,
        }

        while queue:
            current = queue.popleft()

            if current == target:
                break

            x, y = current

            neighbors = [
                (x, y - 1),
                (x, y + 1),
                (x - 1, y),
                (x + 1, y),
            ]

            for neighbor in neighbors:
                if neighbor in previous:
                    continue

                if self.maze.get(neighbor) not in passable:
                    continue

                previous[neighbor] = current
                queue.append(neighbor)

        if target not in previous:
            self.solution = []
            return self.solution

        path: list[Coordinate] = []
        node: Coordinate | None = target

        while node is not None:
            path.append(node)
            node = previous[node]

        path.reverse()
        self.solution = path

        return self.solution

    def get_maze(self) -> Maze:
        """Return the generated maze structure.

        Returns:
            The maze as a coordinate-keyed dictionary.

        Raises:
            RuntimeError: If the maze has not been generated yet.
        """
        if not self.maze:
            raise RuntimeError(
                "Generate the maze before requesting its structure"
            )

        return self.maze

    def get_solution(self) -> list[Coordinate]:
        """Return the solution path.

        Returns:
            The solution as a list of physical coordinates.

        Raises:
            RuntimeError: If the maze has not been generated yet.
        """
        if not self.maze:
            raise RuntimeError(
                "Generate the maze before requesting its solution"
            )

        return self.solution

    def print_maze(self) -> None:
        """Print the generated maze to standard output."""
        if not self.maze:
            raise RuntimeError(
                "Generate the maze before printing it"
            )

        for y in range(self.physical_height):
            for x in range(self.physical_width):
                print(self.maze[x, y], end="")
            print()

        if self.warning_msg:
            print(self.warning_msg)
