

def read_maze_data(filepath: str) -> tuple[str,
                                           tuple[str, str],
                                           tuple[str, str], str]:
    """Reads .txt and separates data"""
    maze_lines = []
    entry_coord = ("0", "0")
    exit_coord = ("0", "0")
    path_str = ""

    with open(filepath, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    entry = 0
    for line in lines:
        stripped = line.strip()

        if not stripped:
            continue
        if "," not in line and entry != 2:
            maze_lines.append(stripped)
        else:
            if entry == 0:
                coords = stripped
                x, y = coords.split(',')
                entry_coord = (x, y)
                entry = 1
            elif entry == 1:
                coords = stripped
                x, y = coords.split(',')
                exit_coord = (x, y)
                entry = 2
            else:
                path_str = stripped

    return maze_lines, entry_coord, exit_coord, path_str
