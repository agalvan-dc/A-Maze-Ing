

def read_maze_data(filepath: str):
    """Lee el archivo .txt y separa el laberinto de las instrucciones."""
    maze_lines = []
    entry = (0, 0)
    exit_coord = (0, 0)
    path_str = ""

    with open(filepath, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    parsing_maze = True
    for line in lines:
        stripped = line.strip()

        if not stripped:
            parsing_maze = False
            continue

        if parsing_maze:
            maze_lines.append(stripped)
        else:
            if "entry" in line:
                coords = stripped.split('#')[0].strip()
                x, y = map(int, coords.split(','))
                entry = (x, y)
            elif "exit" in line:
                coords = stripped.split('#')[0].strip()
                x, y = map(int, coords.split(','))
                exit_coord = (x, y)
            else:
                path_str = stripped

    return maze_lines, entry, exit_coord, path_str
