*This project has been created as part of the 42 curriculum by agalvan-, caperale.*

<div align="center">
  <img src="utilities/a_maze_ing.gif" alt="A-Maze-ing Demo" width="600"/>
</div>

<div align="center">
<i>A_maze_ing 42</i>
</div>

## Description

The A-Maze-ing project is a comprehensive grid-based maze generator and solver. It features both a lightweight 2D terminal display and a fully functional pseudo-3D raycasting engine. The primary goal of this project is to implement robust data structures and algorithms to procedurally generate a perfect maze, solve it using advanced pathfinding techniques, and render the environment efficiently from a first-person perspective.

In addition to the main application, the project provides a reusable Python package named `mazegen`. The package isolates the maze-generation logic from the rendering and application-specific code, allowing the generator to be reused by future Python projects.

---

## Instructions

The project relies on Python and the `poetry` package manager for dependency resolution and execution.

### Compilation and Installation

To configure the environment, install the required development tools (such as `flake8` and `mypy`), and set up the project dependencies via `poetry`, reference the `Makefile` and run:

```bash
make install
````

### Execution

To launch the main program, execute the `a_maze_ing.py` file through the automated rule:

```bash
make run
```

Upon execution, you will be presented with an interactive terminal menu:

1. **Terminal rendering (1):** Displays the generated maze and its solution path directly in the terminal interface. It includes a sub-menu where you can regenerate the maze on the fly or randomize the color palette of the paths and walls.
2. **MLX library (2):** Launches the 3D graphical engine using the MiniLibX (MLX) library, allowing you to explore the generated maze from a first-person perspective.
3. **Exit (3):** Terminates the application safely.

### Cleanup and Linting

The `Makefile` also provides rules for project maintenance:

* `make clean`: Removes Python cache directories, compiled `.pyc` files, the `poetry.lock` file, and generated output files like `utilities/maze_output.txt` and `utilities/processed_map.npy`.
* `make lint` / `make lint-strict`: Runs formatters and static type checkers (`flake8` and `mypy`) to enforce strict code quality and typing standards.

---

## Configuration File Structure

The project dynamically parses a configuration file located at `utilities/config.txt`. The parsed data relies on the following required structure:

* **`width`**: Integer representing the total width of the logical maze grid.
* **`height`**: Integer representing the total height of the logical maze grid.
* **`seed`**: A string or integer used for deterministic random generation. Passing `""`, `"random"`, or `"RANDOM"` disables the seed.
* **`entry`**: A tuple or array defining the logical `(x, y)` starting coordinate.
* **`exit`**: A tuple or array defining the logical `(x, y)` destination coordinate.
* **`perfect`**: A string (`"True"` or `"False"`) dictating whether the generated maze should be a perfect tree structure (no loops) or an imperfect maze with multiple paths.

---

## Algorithms

### Maze Generation

We implemented the **Recursive Backtracking** algorithm for maze generation.

**Why we chose it:** It guarantees the creation of a "perfect" maze—a structure with exactly one unique path between any two points and zero loops. It operates efficiently via Depth-First Search (DFS) carving, making it highly suitable for grid-based memory architectures, and produces visually interesting, long, winding corridors.

### Pathfinding

To navigate and solve the maze automatically, the project implements two core searching algorithms:

**Breadth-First Search (BFS):** An unweighted graph search algorithm that explores the grid radially, layer by layer. In an unweighted grid like our maze, BFS mathematically guarantees finding the absolute shortest path to the exit.

**A-Star Search:** A highly optimized heuristic search algorithm. It guides the search directly towards the exit by calculating the Manhattan distance. It evaluates grid nodes based on the formula:

$$f(n) = g(n) + h(n)$$

Where $g(n)$ is the exact cost from the start node, and $h(n)$ is the estimated heuristic cost to the goal.

---

## Pseudo-3D Raycasting Engine

To render the 2D matrix in a 3D perspective, we built a Raycasting engine utilizing the Digital Differential Analyzer (DDA) algorithm.

### Theoretical Concepts

The screen is divided into vertical stripes. For every $x$-coordinate (representing a vertical stripe on the display), the engine casts a mathematical ray starting from the player's position outward into the 2D map. The ray's vector is determined by the player's viewing direction and a perpendicular 2D camera plane.

### Core Formulas

To map the pixel coordinate to camera space (ranging from -1 to 1):

$$cameraX = \frac{2x}{w} - 1$$

The exact direction of the casted ray is calculated as:

$$rayDirX = dirX + planeX \cdot cameraX$$

$$rayDirY = dirY + planeY \cdot cameraX$$

To iterate through the grid efficiently using DDA, we calculate the scaling factor required for the ray to cross exactly one vertical or horizontal grid boundary:

$$\Delta distX = \left| \frac{1}{rayDirX} \right|$$

$$\Delta distY = \left| \frac{1}{rayDirY} \right|$$

Finally, to prevent the optical "fisheye" distortion (where straight walls appear spherical), we calculate the perpendicular distance to the camera plane rather than the true Euclidean distance:

$$perpWallDist = \frac{mapX - posX + \frac{1 - stepX}{2}}{rayDirX}$$

---

## Architecture and Reusability

A major requirement of this project is that the maze-generation logic can be reused independently from the application that originally uses it.

### Reusable `mazegen` Package

The project provides a standalone Python package named **`mazegen`**.

The reusable maze-generation logic is implemented through a unique public `MazeGenerator` class contained in the package. The generator is independent from the terminal renderer, MLX engine, raycasting implementation, and A-Maze-ing-specific output files.

This separation makes the generator suitable for installation and reuse in a future Python project.

The package can be imported with:

```python
from mazegen import MazeGenerator
```

### Basic Usage

A minimal example of the reusable API is:

```python
from mazegen import MazeGenerator

generator = MazeGenerator(
    width=10,
    height=10,
    seed=42,
)

generator.generate()

maze = generator.maze
solution = generator.solve()

print(maze)
print(solution)
```

The generator follows a simple workflow:

1. Instantiate `MazeGenerator`.
2. Provide the desired generation parameters.
3. Generate the maze with `generate()`.
4. Access the generated structure through `maze`.
5. Obtain a solution path through `solve()`.

### Custom Parameters

The generator supports custom parameters such as maze dimensions and a random seed.

For example:

```python
from mazegen import MazeGenerator

generator = MazeGenerator(
    width=20,
    height=15,
    seed=1234,
)

generator.generate()
```

Using a fixed seed makes the maze generation deterministic and reproducible. This is particularly useful for testing, debugging, and applications that require predictable maze layouts.

When no seed is provided, the generator can produce a different maze for each execution.

### Accessing the Generated Structure

The generated logical maze can be accessed directly after generation:

```python
generator.generate()

maze = generator.maze
```

The structure exposed by the reusable module is intended to be consumed programmatically by another Python application.

It does not need to use the same representation as the textual output generated by the A-Maze-ing application. Keeping these representations separate prevents the reusable package from becoming dependent on application-specific file formats.

### Accessing a Solution

Once the maze has been generated, a solution path can be obtained with:

```python
generator.generate()

solution = generator.solve()
```

The solution can be used by another project to:

* Display the path in a terminal.
* Render the path graphically.
* Calculate the path length.
* Animate a player through the maze.
* Perform additional maze or pathfinding analysis.

### Building the Package

The package is configured as a standard Python package using Poetry.

The project contains the required `pyproject.toml` configuration and build
dependencies, allowing the package to be rebuilt from source during evaluation.

To build the package, run:

```bash
poetry build
```

The resulting distribution files are generated in the `dist/` directory:

```text
dist/
├── mazegen-1.0.0-py3-none-any.whl
└── mazegen-1.0.0.tar.gz
```

The wheel can then be installed in another Python environment using:

```bash
pip install dist/mazegen-1.0.0-py3-none-any.whl
```

The source distribution can also be installed with:

```bash
pip install dist/mazegen-1.0.0.tar.gz
```

### Reuse in Another Project

After installation, a future project only needs to import the generator:

```python
from mazegen import MazeGenerator
```

The reusable package does not require the importing project to use the
A-Maze-ing application's rendering system.

The generator is independent from:

* Terminal rendering.
* ANSI color handling.
* MiniLibX.
* The pseudo-3D raycasting engine.
* `.xpm` textures.
* A-Maze-ing configuration files.
* A-Maze-ing-specific output files.

This provides a clear separation between the algorithmic maze generator and
the application that consumes its output.

### Package Documentation

The reusable module contains its own documentation explaining:

* How to instantiate `MazeGenerator`.
* How to generate a maze.
* How to provide custom parameters such as dimensions and seeds.
* How to access the generated maze structure.
* How to obtain a solution path.
* How to install and reuse the package.

This documentation is intended to make the package usable independently of
the main A-Maze-ing application.

### Advanced Features

The main project seamlessly supports multiple rendering modes:

* Terminal / ANSI 2D rendering.
* MLX pseudo-3D rendering.

The application also allows real-time maze modification, including
instantaneous dynamic regeneration and color palette randomization.

---

## Team and Project Management

### Roles

**agalvan-**: Developed all visual display mechanics. This includes the dynamic terminal rendering pipeline, the integration of the MLX library wrapper, and the full mathematical implementation of the 3D raycasting engine.

**caperale**: Designed the underlying data architecture, implemented the Recursive Backtracking (DFS) generation algorithm, and built the A* pathfinding solvers.

### Planning and Evolution

Our development pipeline began with a low-level prototyping phase. We built the initial raycasting engine in **C** using the **SDL** library. This approach forced us to fully grasp the memory management, pointer arithmetic, and mathematical complexities of the DDA algorithm. Once the mathematical foundation was proven solid, we migrated the architecture to Python and bound it to the 42 MLX library.

### What Worked and What Could Be Improved

**What worked well:** Decoupling the data structure from the visual engine was highly effective. It allowed us to work in parallel on the algorithmic backend and the 3D frontend without causing Git merge conflicts or logical bottlenecks.

The additional separation of the maze generator into the reusable `mazegen` package further improves the architecture by allowing the generation algorithm to be distributed independently from the graphical application.

**What could be improved:** Python's inherent interpretation overhead caused minor performance dips during the heaviest raycasting mathematical loops. Refactoring the pixel-by-pixel DDA loop to utilize fully vectorized NumPy operations would significantly increase the engine's frame rate.

`Sisiphus.xpm` should be implemented in future versions, throughout the maze or in the exit step.

### Specific Tools

**C and SDL:** Used exclusively during the early prototyping phase to validate the raycasting mathematics.

**Lodev's Raycasting Tutorial:** Acted as our primary mathematical blueprint for pseudo-3D rendering.

---

## License

This project, including the reusable `mazegen` package, is licensed under the **GNU General Public License v3.0 (GPLv3)**.

The GNU GPLv3 is a free and open-source software license that allows the code to be **used, studied, modified, and redistributed**.

Any future project that incorporates or distributes the GPLv3-licensed `mazegen` code must preserve the freedoms granted by the license and comply with the terms and conditions of the GNU GPLv3.

The complete license text is available in the [`LICENSE.md`](LICENSE.md) file at the root of this repository.

The license explicitly permits the reuse and distribution of the maze generator by future projects, while ensuring that the corresponding GPLv3 licensing conditions are respected.

---

## Resources

**Documentation & Tutorials:** We heavily utilized Lodev's Computer Graphics Tutorial as the classic reference for understanding the linear algebra behind DDA and raycasting.

**AI Usage:** Artificial Intelligence was employed strictly as a debugging assistant and syntax translator. It was used to diagnose memory padding and stride alignment issues when reading `.xpm` textures via the MLX wrapper, and to receive structural recommendations when porting our initial C/SDL prototypes into idiomatic, object-oriented Python.
