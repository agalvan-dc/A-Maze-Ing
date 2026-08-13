import random
import os
from .maze_solver import MazeSolver
from .parsing import validate_conf


class MazeGenerator:
    def __init__(self, config_path: str = "./utilities/config.txt"):
        # Atributos/Constantes de la clase
        self.EMPTY = ' '
        self.MARK = '@'
        self.WALL = chr(9608)
        self.FORTY_TWO = "\033[48;5;208m \033[0m"
        self.NORTH, self.SOUTH, self.EAST, self.WEST = "n", "s", "e", "w"
        self.BLUE = "\033[44m \033[0m"
        self.RED = "\033[41m \033[0m"
        self.config_path = os.path.expanduser(config_path)
        self.warning_msg: str | None

    def get_config(self) -> dict:
        return validate_conf(self.config_path)

    def put_ft_in_maze(self, maze, width, height) -> None:
        # creación del 42 de en medio
        if width >= 9 and height >= 9:
            width_center = int(width / 2)
            height_center = int(height / 2)
            maze[(width_center - 1, height_center)] = self.FORTY_TWO
            maze[(width_center - 2, height_center)] = self.FORTY_TWO
            maze[(width_center - 3, height_center)] = self.FORTY_TWO
            maze[(width_center - 3, height_center - 1)] = self.FORTY_TWO
            maze[(width_center - 3, height_center - 2)] = self.FORTY_TWO
            maze[(width_center - 1, height_center + 1)] = self.FORTY_TWO
            maze[(width_center - 1, height_center + 2)] = self.FORTY_TWO
            maze[(width_center + 1, height_center)] = self.FORTY_TWO
            maze[(width_center + 2, height_center)] = self.FORTY_TWO
            maze[(width_center + 3, height_center)] = self.FORTY_TWO
            maze[(width_center + 1, height_center + 2)] = self.FORTY_TWO
            maze[(width_center + 2, height_center + 2)] = self.FORTY_TWO
            maze[(width_center + 3, height_center + 2)] = self.FORTY_TWO
            maze[(width_center + 1, height_center + 1)] = self.FORTY_TWO
            maze[(width_center + 1, height_center - 2)] = self.FORTY_TWO
            maze[(width_center + 2, height_center - 2)] = self.FORTY_TWO
            maze[(width_center + 3, height_center - 2)] = self.FORTY_TWO
            maze[(width_center + 3, height_center - 1)] = self.FORTY_TWO
            maze[(width_center, height_center)] = self.EMPTY
            maze[(width_center, height_center + 1)] = self.EMPTY
            maze[(width_center, height_center + 2)] = self.EMPTY
            maze[(width_center + 2, height_center + 1)] = self.EMPTY
            maze[(width_center + 2, height_center - 1)] = self.EMPTY
            maze[(width_center - 2, height_center - 1)] = self.EMPTY
            maze[(width_center - 2, height_center - 2)] = self.EMPTY
            maze[(width_center - 2, height_center + 1)] = self.EMPTY
            maze[(width_center - 2, height_center + 2)] = self.EMPTY
            maze[(width_center - 1, height_center - 1)] = self.EMPTY
            maze[(width_center + 1, height_center - 1)] = self.EMPTY
            maze[(width_center + 3, height_center + 1)] = self.EMPTY

    def do_basic(self, dict_data, maze) -> dict[tuple[int, int], str]:
        # valores del diccionario
        width = int(dict_data['width']) * 2 + 1
        height = int(dict_data['height']) * 2 + 1
        entry = dict_data['entry']
        exit_pos = dict_data['exit']
        perfect = dict_data['perfect']
        seed = dict_data['seed']

        if seed and seed != "" and seed != "random" and seed != "RANDOM":
            random.seed(seed)
        else:
            random.seed()

        if exit_pos > (width, height) or exit_pos < (0, 0):
            raise Exception("exit coords invalid, please put a number between"
                            " width and height")
        elif entry > (width, height) or entry < (0, 0):
            raise Exception("entry coords invalid, please put a number between"
                            " width and height")


        # inicio del algoritmo
        if width > 9 and height > 9:
            self.put_ft_in_maze(maze, width, height)

        if width <= 9 or height <= 9:
            self.warning_msg = "Can't put 42 in maze"

        has_visited = []  # tabla de marcado

        def visit(x, y) -> None:
            nextX, nextY = 0, 0
            if maze.get((x, y)) != self.FORTY_TWO:  # proteccion del 42
                maze[(x, y)] = self.EMPTY
            while True:
                unvisitedNeighbors = []

                # Solo añadir la dirección si el destino Y el muro intermedio NO son FORTY_TWO
                if y - 2 >= 1 and (x, y - 2) not in has_visited:
                    if maze.get((x, y - 2)) != self.FORTY_TWO and maze.get((x, y - 1)) != self.FORTY_TWO:
                        unvisitedNeighbors.append(self.NORTH)

                if y + 2 < height - 1 and (x, y + 2) not in has_visited:
                    if maze.get((x, y + 2)) != self.FORTY_TWO and maze.get((x, y + 1)) != self.FORTY_TWO:
                        unvisitedNeighbors.append(self.SOUTH)

                if x - 2 >= 1 and (x - 2, y) not in has_visited:
                    if maze.get((x - 2, y)) != self.FORTY_TWO and maze.get((x - 1, y)) != self.FORTY_TWO:
                        unvisitedNeighbors.append(self.WEST)

                if x + 2 < width - 1 and (x + 2, y) not in has_visited:
                    if maze.get((x + 2, y)) != self.FORTY_TWO and maze.get((x + 1, y)) != self.FORTY_TWO:
                        unvisitedNeighbors.append(self.EAST)

                if len(unvisitedNeighbors) == 0:
                    return
                else:
                    next_tile = random.choice(unvisitedNeighbors)
                    if next_tile == self.NORTH:
                        nextX, nextY = x, y - 2
                        maze[(x, y - 1)] = self.EMPTY
                    elif next_tile == self.SOUTH:
                        nextX, nextY = x, y + 2
                        maze[(x, y + 1)] = self.EMPTY
                    elif next_tile == self.WEST:
                        nextX, nextY = x - 2, y
                        maze[(x - 1, y)] = self.EMPTY
                    elif next_tile == self.EAST:
                        nextX, nextY = x + 2, y
                        maze[(x + 1, y)] = self.EMPTY

                    has_visited.append((nextX, nextY))
                    visit(nextX, nextY)

        has_visited = [entry]  # empezamos por donde diga el config
        visit(1, 1)
        if perfect == 'False' or perfect is False:
            # Recorremos todas las celdas de camino transitables (coordenadas impares)
            for y in range(1, height - 1, 2):
                for x in range(1, width - 1, 2):
                    if maze[(x, y)] == self.EMPTY:

                        # 1. Contamos los muros inmediatos (distancia 1)
                        wall_neighbors = []
                        if maze.get((x, y - 1)) in (self.WALL, self.FORTY_TWO):
                            wall_neighbors.append(self.NORTH)
                        if maze.get((x, y + 1)) in (self.WALL, self.FORTY_TWO):
                            wall_neighbors.append(self.SOUTH)
                        if maze.get((x - 1, y)) in (self.WALL, self.FORTY_TWO):
                            wall_neighbors.append(self.WEST)
                        if maze.get((x + 1, y)) in (self.WALL, self.FORTY_TWO):
                            wall_neighbors.append(self.EAST)

                        # 2. Si tiene 3 muros a distancia 1, es un callejón sin salida real
                        if len(wall_neighbors) == 3:
                            secure_options = []

                            # Filtramos las direcciones para quedarnos SOLO con muros internos.
                            if self.NORTH in wall_neighbors and y > 1 and maze.get((x, y - 1)) == self.WALL:
                                secure_options.append(self.NORTH)
                            if self.SOUTH in wall_neighbors and y < height - 2 and maze.get((x, y + 1)) == self.WALL:
                                secure_options.append(self.SOUTH)
                            if self.WEST in wall_neighbors and x > 1 and maze.get((x - 1, y)) == self.WALL:
                                secure_options.append(self.WEST)
                            if self.EAST in wall_neighbors and x < width - 2 and maze.get((x + 1, y)) == self.WALL:
                                secure_options.append(self.EAST)

                            # 3. Si hay opciones seguras, elegimos una al azar y rompemos el muro intermedio
                            if secure_options:
                                wall_to_break = random.choice(secure_options)
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

    def generate_maze(self, input_dict: dict,
                      algo: str = "basic") -> dict[tuple[int, int], str]:
        width = int(input_dict['width']) * 2 + 1
        height = int(input_dict['height']) * 2 + 1

        # laberinto con todo muros
        maze = {}
        for y in range(height):
            for x in range(width):
                maze[(x, y)] = self.WALL

        # elegimos algoritmo
        if algo == "basic":
            maze = self.do_basic(input_dict, maze)
        elif algo == "prueba":
            exit()
        else:
            exit()
        return maze

    def print_maze(self, maze) -> None:
        width = max(coor[0] for coor in maze.keys()) + 1
        height = max(coor[1] for coor in maze.keys()) + 1
        for y in range(height):
            for x in range(width):
                print(maze[x, y], end="")
            print()
        if self.warning_msg:
            print(self.warning_msg)


if __name__ == "__main__":
    try:
        # 1. Cargar configuración y generar laberinto
        generator = MazeGenerator()
        config_data = generator.temp_dict()
        maze = generator.generate_maze(config_data, "basic")

        # 2. Obtener dimensiones
        width = max(coor[0] for coor in maze.keys()) + 1
        height = max(coor[1] for coor in maze.keys()) + 1

        # 3. Mismas transformaciones de coordenadas que hace do_basic
        entry = tuple(map(int, config_data['entry'].split(',')))
        exit_pos = tuple(map(lambda c: int(c) * 2 + 1,
                             config_data['exit'].split(',')))

        # 4. Resolver
        solver = MazeSolver(maze, entry, exit_pos)
        path = solver.a_star(maze, entry, exit_pos, width, height)

        # 5. Pintar camino si se encontró solución
        if path:
            for pos in path[1:-1]:
                maze[pos] = solver.solve_color
        else:
            print("No se encontró un camino válido.")

        # 6. Imprimir
        generator.print_maze(maze)

    except Exception:
        import traceback
        traceback.print_exc()  # Nos dará la línea exacta si vuelve a fallar
