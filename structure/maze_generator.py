import numpy as np
from pathlib import Path
import random


def generate_maze(input: str) -> str:
    config_dict = {}
    with open(input, "r", encoding='utf-8') as config:
        for line in config:
            if not line.strip():
                continue

            key, value = line.strip().split("=")
            config_dict[key.strip()] = value.strip()

    #diccionario temporal, luego se usara input con uno valido parseado
    width = config_dict['WIDTH']
    height = config_dict['HEIGHT']
    entry = config_dict['ENTRY']
    exit = config_dict['EXIT']
    output_file = config_dict['OUTPUT_FILE']
    perfect = config_dict['PERFECT']

    #caracteres para el display del laberinto en terminal
    EMPTY = ' '
    MARK = '@'
    WALL = chr(9608)
    NORTH, SOUTH, EAST, WEST = n, s, e, w

    return "utilities/output_maze.txt"


generate_maze("/home/caperale/milestone2/amazeing/utilities/config.txt")