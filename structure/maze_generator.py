import numpy as np
from pathlib import Path
import random

EMPTY = ' '
MARK = '@'
WALL = chr(9608)
FORTY_TWO = "\033[48;5;208m \033[0m"
NORTH, SOUTH, EAST, WEST = "n", "s", "e", "w"
BLUE = "\033[44m \033[0m"
RED = "\033[41m \033[0m"


def temp_dict() -> dict:
    config_dict = {}
    with open("/home/caperale/milestone2/amazeing/utilities/config.txt",
              "r",
              encoding='utf-8') as config:
        for line in config:
            if not line.strip():
                continue

            key, value = line.strip().split("=")
            config_dict[key.strip()] = value.strip()
        return config_dict

def put_ft_in_maze(maze, width, height) -> None:
    # creación del 42 de en medio
    if width >= 9 and height >= 9:
        width_center = int(width / 2)
        height_center = int(height / 2)
        maze[(width_center - 1, height_center)] = FORTY_TWO
        maze[(width_center - 2, height_center)] = FORTY_TWO
        maze[(width_center - 3, height_center)] = FORTY_TWO
        maze[(width_center - 3, height_center - 1)] = FORTY_TWO
        maze[(width_center - 3, height_center - 2)] = FORTY_TWO
        maze[(width_center - 1, height_center + 1)] = FORTY_TWO
        maze[(width_center - 1, height_center + 2)] = FORTY_TWO
        maze[(width_center + 1, height_center)] = FORTY_TWO
        maze[(width_center + 2, height_center)] = FORTY_TWO
        maze[(width_center + 3, height_center)] = FORTY_TWO
        maze[(width_center + 1, height_center + 2)] = FORTY_TWO
        maze[(width_center + 2, height_center + 2)] = FORTY_TWO
        maze[(width_center + 3, height_center + 2)] = FORTY_TWO
        maze[(width_center + 1, height_center + 1)] = FORTY_TWO
        maze[(width_center + 1, height_center - 2)] = FORTY_TWO
        maze[(width_center + 2, height_center - 2)] = FORTY_TWO
        maze[(width_center + 3, height_center - 2)] = FORTY_TWO
        maze[(width_center + 3, height_center - 1)] = FORTY_TWO
        maze[(width_center, height_center)] = EMPTY
        maze[(width_center, height_center + 1)] = EMPTY
        maze[(width_center, height_center + 2)] = EMPTY
        maze[(width_center + 2, height_center + 1)] = EMPTY
        maze[(width_center + 2, height_center - 1)] = EMPTY
        maze[(width_center - 2, height_center - 1)] = EMPTY

def do_basic(dict, maze) -> dict[tuple[int, int], str]:
    # valores del diccionario
    width = int(dict['WIDTH']) * 2 + 1
    height = int(dict['HEIGHT']) * 2 + 1
    entry = tuple(map(int, dict['ENTRY'].split(',')))
    exit = tuple(map(lambda c: int(c) * 2 + 1, dict['EXIT'].split(',')))
    output_file = dict['OUTPUT_FILE']
    perfect = dict['PERFECT']

    # inicio del algoritmo
    put_ft_in_maze(maze, width, height)
    has_visited = []  # tabla de marcado
    def visit(x, y) -> None:
        if maze.get((x, y)) != FORTY_TWO:  # proteccion del 42
            maze[(x, y)] = EMPTY
        while True:
            unvisitedNeighbors = []
            
            # Solo añadir la dirección si el destino Y el muro intermedio NO son FORTY_TWO
            if y - 2 >= 1 and (x, y - 2) not in has_visited:
                if maze.get((x, y - 2)) != FORTY_TWO and maze.get((x, y - 1)) != FORTY_TWO:
                    unvisitedNeighbors.append(NORTH)
                    
            if y + 2 < height - 1 and (x, y + 2) not in has_visited:
                if maze.get((x, y + 2)) != FORTY_TWO and maze.get((x, y + 1)) != FORTY_TWO:
                    unvisitedNeighbors.append(SOUTH)
                    
            if x - 2 >= 1 and (x - 2, y) not in has_visited:
                if maze.get((x - 2, y)) != FORTY_TWO and maze.get((x - 1, y)) != FORTY_TWO:
                    unvisitedNeighbors.append(WEST)
                    
            if x + 2 < width - 1 and (x + 2, y) not in has_visited:
                if maze.get((x + 2, y)) != FORTY_TWO and maze.get((x + 1, y)) != FORTY_TWO:
                    unvisitedNeighbors.append(EAST)

            if len(unvisitedNeighbors) == 0:
                return
            else:
                next_tile = random.choice(unvisitedNeighbors)
                if next_tile == NORTH:
                    nextX, nextY = x, y - 2
                    maze[(x, y - 1)] = EMPTY
                elif next_tile == SOUTH:
                    nextX, nextY = x, y + 2
                    maze[(x, y + 1)] = EMPTY
                elif next_tile == WEST:
                    nextX, nextY = x - 2, y
                    maze[(x - 1, y)] = EMPTY
                elif next_tile == EAST:
                    nextX, nextY = x + 2, y
                    maze[(x + 1, y)] = EMPTY

                has_visited.append((nextX, nextY))
                visit(nextX, nextY)
    has_visited = [entry]  # empezamos por donde diga el config
    visit(1, 1)
    if perfect == 'False' or perfect is False:
        # Recorremos todas las celdas de camino transitables (coordenadas impares)
        for y in range(1, height - 1, 2):
            for x in range(1, width - 1, 2):
                if maze[(x, y)] == EMPTY:
                    
                    # 1. Contamos los muros inmediatos (distancia 1)
                    wall_neighbors = []
                    if maze.get((x, y - 1)) in (WALL, FORTY_TWO):
                        wall_neighbors.append(NORTH)
                    if maze.get((x, y + 1)) in (WALL, FORTY_TWO):
                        wall_neighbors.append(SOUTH)
                    if maze.get((x - 1, y)) in (WALL, FORTY_TWO):
                        wall_neighbors.append(WEST)
                    if maze.get((x + 1, y)) in (WALL, FORTY_TWO):
                        wall_neighbors.append(EAST)

                    # 2. Si tiene 3 muros a distancia 1, es un callejón sin salida real
                    if len(wall_neighbors) == 3:
                        secure_options = []
                        
                        # Filtramos las direcciones para quedarnos SOLO con muros internos.
                        # Evitamos por completo tocar el perímetro exterior (y=0, y=height-1, x=0, x=width-1)
                        if NORTH in wall_neighbors and y > 1 and maze.get((x, y - 1)) == WALL: 
                            secure_options.append(NORTH)
                        if SOUTH in wall_neighbors and y < height - 2 and maze.get((x, y + 1)) == WALL: 
                            secure_options.append(SOUTH)
                        if WEST in wall_neighbors and x > 1 and maze.get((x - 1, y)) == WALL: 
                            secure_options.append(WEST)
                        if EAST in wall_neighbors and x < width - 2 and maze.get((x + 1, y)) == WALL: 
                            secure_options.append(EAST)

                        # 3. Si hay opciones seguras, elegimos una al azar y rompemos el muro intermedio
                        if secure_options:
                            wall_to_break = random.choice(secure_options)
                            if wall_to_break == NORTH:
                                maze[(x, y - 1)] = EMPTY
                            elif wall_to_break == SOUTH:
                                maze[(x, y + 1)] = EMPTY
                            elif wall_to_break == WEST:
                                maze[(x - 1, y)] = EMPTY
                            elif wall_to_break == EAST:
                                maze[(x + 1, y)] = EMPTY
    maze[entry] = BLUE
    maze[exit] = RED
    return maze


def generate_maze(input: dict, algo: str = "basic") -> dict[tuple[int, int], str]:
    # diccionario temporal, luego se usara input con uno valido parseado
    width = int(input['WIDTH']) * 2 + 1
    height = int(input['HEIGHT']) * 2 + 1
    entry = input['ENTRY']
    exit = input['EXIT']
    output_file = input['OUTPUT_FILE']
    perfect = input['PERFECT']

    # caracter utilizado para el muro
    WALL = chr(9608)

    # laberinto con todo muros
    maze = {}
    for y in range(height):
        for x in range(width):
            maze[(x, y)] = WALL

    # elegimos algoritmo
    if (algo == "basic"):
        maze = do_basic(input, maze)
    elif (algo == "prueba"):
        exit()
    else:
        exit()
    return maze


def print_maze(maze) -> None:
    width = max(coor[0] for coor in maze.keys()) + 1
    height = max(coor[1] for coor in maze.keys()) + 1
    for y in range(height):
        for x in range(width):
            print(maze[x, y], end="")
        print()


dict = temp_dict()
maze = generate_maze(dict, "basic")
print_maze(maze)
