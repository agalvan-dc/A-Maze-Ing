import random
import numpy as np
from MazeModel import MazeModel as maze_model

class MazeSolver:
    def __init__(self, maze: maze_model,
                 entry: tuple[int, int],
                 exit: tuple[int ,int]) -> None:
        self.maze = maze
        self.solve_color = "\033[48;5;201m \033[0m"
        self.entry = entry
        self.exit = exit

        self.path = []
        self.visited = []
        self.a_star()

    def get_path(self):
        return self.path

    def get_visited(self):
        return self.visited

    @staticmethod
    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def a_star(self):
        open_list = [self.entry]
        visited_set = set()
        g_score = {self.entry: 0}
        f_score = {self.entry: self.heuristic(self.entry, self.exit)}
        came_from = {}

        while open_list:
            current = min(open_list, key=lambda node:
                          f_score.get(node, float('inf')))

            if current == self.exit:
                # reconstruimos el camino y lo devolvemos a la inversa
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(self.entry)
                self.path = path[::-1]
                return self.path

            open_list.remove(current)
            visited_set.add(current)

            self.visited.append(current)
            # vecinos
            neighbors = [
                (current[0] + 1, current[1]),
                (current[0] - 1, current[1]),
                (current[0], current[1] + 1),
                (current[0], current[1] - 1),
            ]

            for neighbor in neighbors:
                r, c = neighbor

                if neighbor in visited_set:
                    continue

                if 0 <= r < self.maze.cols and 0 <= c < self.maze.rows:
                    if not self.maze.is_wall(r, c):
                        tentative_g_score = g_score[current] + 1

                        if (neighbor not in g_score
                                or tentative_g_score < g_score[neighbor]):
                            came_from[neighbor] = current
                            g_score[neighbor] = tentative_g_score
                            f_score[neighbor] = (tentative_g_score +
                                                 self.heuristic(neighbor, exit))
                            if neighbor not in open_list:
                                open_list.append(neighbor)
        self.path = []
        return []
