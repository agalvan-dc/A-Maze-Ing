import random
import numpy as np

class MazeSolver:
    def __init__(self, maze, entry, exit):
        self.maze = maze
        self.solve_color = "\033[48;5;201m \033[0m"
        self.entry = entry
        self.exit = exit

    @staticmethod
    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def a_star(self, maze, entry, exit, width, height):
        open_list = [entry]
        visited = set()
        g_score = {entry: 0}
        f_score = {entry: self.heuristic(entry, exit)}
        came_from = {}

        while open_list:
            current = min(open_list, key=lambda node:
                          f_score.get(node, float('inf')))

            if current == exit:
                # reconstruimos el camino y lo devolvemos a la inversa
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(entry)
                return path[::-1]

            open_list.remove(current)
            visited.add(current)
            # vecinos
            neighbors = [
                (current[0] + 1, current[1]),
                (current[0] - 1, current[1]),
                (current[0], current[1] + 1),
                (current[0], current[1] - 1),
            ]

            for neighbor in neighbors:
                r, c = neighbor

                if neighbor in visited:
                    continue

                if 0 <= r < width and 0 <= c < height:
                    tile = maze.get(neighbor)
                    if tile != chr(9608) and tile != "\033[48;5;208m \033[0m":
                        tentative_g_score = g_score[current] + 1

                        if (neighbor not in g_score
                                or tentative_g_score < g_score[neighbor]):
                            came_from[neighbor] = current
                            g_score[neighbor] = tentative_g_score
                            f_score[neighbor] = (tentative_g_score +
                                                 self.heuristic(neighbor, exit))
                            if neighbor not in open_list:
                                open_list.append(neighbor)

        return []
