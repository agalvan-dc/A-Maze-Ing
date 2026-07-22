import numpy as np
from pathlib import Path
import random

EMPTY = ' '
MARK = '@'
WALL = chr(9608)
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


def do_basic(dict, maze) -> dict[tuple[int, int], str]:
    # valores del diccionario
    width = int(dict['WIDTH']) * 2 + 1
    height = int(dict['HEIGHT']) * 2 + 1
    entry = tuple(map(int, dict['ENTRY'].split(',')))
    exit = tuple(map(lambda c: int(c) * 2 + 1, dict['EXIT'].split(',')))
    output_file = dict['OUTPUT_FILE']
    perfect = dict['PERFECT']

    # inicio del algoritmo
    has_visited = []  # tabla de marcado
    def visit(x, y) -> None:
        maze[(x, y)] = EMPTY  # crear espacio
        while True:
            unvisitedNeighbors = []  # posibles caminos
            if y - 2 >= 1 and (x, y - 2) not in has_visited:
                unvisitedNeighbors.append(NORTH)
            if y + 2 < height - 1 and (x, y + 2) not in has_visited:
                unvisitedNeighbors.append(SOUTH)
            if x - 2 >= 1 and (x - 2, y) not in has_visited:
                unvisitedNeighbors.append(WEST)
            if x + 2 < width - 1 and (x + 2, y) not in has_visited:
                unvisitedNeighbors.append(EAST)

            if len(unvisitedNeighbors) == 0:
                #caso base (dead end)
                return
            else:
                #caso recursivo
                next_tile = random.choice(unvisitedNeighbors)

                if next_tile == NORTH:
                    nextX = x
                    nextY = y - 2
                    maze[(x, y - 1)] = EMPTY
                elif next_tile == SOUTH:
                    nextX = x
                    nextY = y + 2
                    maze[(x, y + 1)] = EMPTY
                elif next_tile == WEST:
                    nextX = x - 2
                    nextY = y
                    maze[(x - 1, y)] = EMPTY
                elif next_tile == EAST:
                    nextX = x + 2
                    nextY = y
                    maze[(x + 1, y)] = EMPTY
                has_visited.append((nextX, nextY))  # marcamos como visitado
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
                    if maze[(x, y - 1)] == WALL: wall_neighbors.append(NORTH)
                    if maze[(x, y + 1)] == WALL: wall_neighbors.append(SOUTH)
                    if maze[(x - 1, y)] == WALL: wall_neighbors.append(WEST)
                    if maze[(x + 1, y)] == WALL: wall_neighbors.append(EAST)

                    # 2. Si tiene 3 muros a distancia 1, es un callejón sin salida real
                    if len(wall_neighbors) == 3:
                        secure_options = []
                        
                        # Filtramos las direcciones para quedarnos SOLO con muros internos.
                        # Evitamos por completo tocar el perímetro exterior (y=0, y=height-1, x=0, x=width-1)
                        if NORTH in wall_neighbors and y > 1: secure_options.append(NORTH)
                        if SOUTH in wall_neighbors and y < height - 2: secure_options.append(SOUTH)
                        if WEST in wall_neighbors and x > 1: secure_options.append(WEST)
                        if EAST in wall_neighbors and x < width - 2: secure_options.append(EAST)

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
