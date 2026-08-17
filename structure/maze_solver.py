from typing import Dict, List, Tuple

Coordinate = Tuple[int, int]
Maze = Dict[Coordinate, str]


class MazeSolver:
    def __init__(
        self,
        maze: Maze,
        entry: Coordinate,
        exit: Coordinate
    ) -> None:
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

        self.path: List[Coordinate] = []
        self.visited: List[Coordinate] = []

        self.a_star()

    def get_cell(self, x: int, y: int):
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
        y2: int
    ) -> bool:
        """
        Comprueba si se puede mover entre dos celdas LÓGICAS.

        Las coordenadas recibidas son lógicas.
        Se convierten a físicas para consultar self.maze.
        """

        # Primero comprobamos que el destino está dentro
        # de las dimensiones lógicas.
        if not (
            0 <= x2 < self.width
            and 0 <= y2 < self.height
        ):
            return False

        # Coordenada física de origen.
        px1 = x1 * 2 + 1
        py1 = y1 * 2 + 1

        # Coordenada física de destino.
        px2 = x2 * 2 + 1
        py2 = y2 * 2 + 1

        # La celda destino está bloqueada.
        if self.is_wall(px2, py2):
            return False

        # Coordenada física del muro/camino entre ambas
        # celdas lógicas.
        mx = (px1 + px2) // 2
        my = (py1 + py2) // 2

        if self.is_wall(mx, my):
            return False

        return True

    def get_path(self) -> List[Coordinate]:
        return self.path

    def get_visited(self) -> List[Coordinate]:
        return self.visited

    @staticmethod
    def heuristic(
        a: Coordinate,
        b: Coordinate
    ) -> int:
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def a_star(self) -> List[Coordinate]:
        """
        A* trabajando EXCLUSIVAMENTE con coordenadas lógicas.

        Ejemplo:
            (0, 0) -> (1, 0) -> (1, 1)

        No trabaja directamente con:
            (1, 1) -> (3, 1) -> (3, 3)
        """

        # Comprobar entry y exit antes de empezar.
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

        open_list: List[Coordinate] = [self.entry]

        visited_set = set()

        g_score = {
            self.entry: 0
        }

        f_score = {
            self.entry: self.heuristic(
                self.entry,
                self.exit
            )
        }

        came_from: Dict[Coordinate, Coordinate] = {}

        while open_list:

            current = min(
                open_list,
                key=lambda node: f_score.get(
                    node,
                    float("inf")
                )
            )

            if current == self.exit:
                path: List[Coordinate] = []

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

            neighbors = [
                (x + 1, y),  # E
                (x - 1, y),  # W
                (x, y + 1),  # S
                (x, y - 1),  # N
            ]

            for neighbor in neighbors:
                nx, ny = neighbor

                # Fuera del laberinto lógico.
                if not (
                    0 <= nx < self.width
                    and 0 <= ny < self.height
                ):
                    continue

                if neighbor in visited_set:
                    continue

                # Comprueba el destino y el muro intermedio.
                if not self.can_move(
                    x,
                    y,
                    nx,
                    ny
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
                            self.exit
                        )
                    )

                    if neighbor not in open_list:
                        open_list.append(neighbor)

        self.path = []
        return []

    def get_cell_hex(self, x: int, y: int) -> str:
        """
        Convierte una celda LÓGICA a su representación hexadecimal.

        x, y son coordenadas lógicas.
        self.maze utiliza coordenadas físicas.
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

        cell = self.maze[physical_x, physical_y]

        # FORTY_TWO ocupa una celda lógica completa.
        if cell == self.forty_two:
            return "F"

        walls = 0

        # Norte.
        if self.is_wall(
            physical_x,
            physical_y - 1
        ):
            walls |= 1

        # Este.
        if self.is_wall(
            physical_x + 1,
            physical_y
        ):
            walls |= 2

        # Sur.
        if self.is_wall(
            physical_x,
            physical_y + 1
        ):
            walls |= 4

        # Oeste.
        if self.is_wall(
            physical_x - 1,
            physical_y
        ):
            walls |= 8

        return format(walls, "X")

    def path_to_directions(self) -> str:
        """
        Convierte el path lógico en direcciones.

        Como A* trabaja en coordenadas lógicas, cada movimiento
        del path corresponde directamente a una dirección.

        Ejemplo:

            (0,0) -> (1,0) -> (1,1)

        produce:

            ES
        """

        directions: List[str] = []

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
        """
        Escribe maze_output.txt usando exclusivamente
        coordenadas lógicas en el fichero.
        """

        with open(filename, "w", encoding="utf-8") as file:

            # El fichero contiene WIDTH x HEIGHT celdas lógicas.
            for y in range(self.height):
                line = ""

                for x in range(self.width):
                    line += self.get_cell_hex(x, y)

                file.write(line + "\n")

            # Línea vacía.
            file.write("\n")

            # Entry ya está en coordenadas lógicas.
            file.write(
                f"{self.entry[0]},{self.entry[1]}\n"
            )

            # Exit ya está en coordenadas lógicas.
            file.write(
                f"{self.exit[0]},{self.exit[1]}\n"
            )

            # Camino lógico.
            file.write(
                self.path_to_directions() + "\n"
            )
