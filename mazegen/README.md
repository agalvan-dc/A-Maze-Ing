*This project has been created as part of the 42 curriculum by agalvan-, caperale.*
# mazegen

Reusable Python package for procedural maze generation.

`mazegen` contains the reusable maze-generation logic developed for the
**A-Maze-ing** project. The generator is intentionally independent from the
terminal renderer, MiniLibX, raycasting engine, and project-specific file
formats, so it can be reused by other Python projects.

## Features

- Procedural maze generation using recursive backtracking / DFS.
- Configurable maze dimensions.
- Optional deterministic generation using a custom seed.
- Access to the generated maze structure.
- Access to a solution path from the entrance to the exit.
- No dependency on the project's rendering or graphical systems.
- Installable as a standard Python package with `pip`.

## Installation

The package can be installed from the generated wheel:

```bash
pip install mazegen-1.0.0-py3-none-any.whl
````

It can also be installed from the generated source distribution:

```bash
pip install mazegen-1.0.0.tar.gz
```

The package can be built from the project sources with:

```bash
poetry build
```

The generated distributions will be placed in the `dist/` directory.

## Basic Usage

The main public API is the `MazeGenerator` class.

```python
from mazegen import MazeGenerator

generator = MazeGenerator(width=10, height=10)

maze = generator.generate()
solution = generator.solve()

print(maze)
print(solution)
```

The generator can therefore be used without importing any of the rendering
or application-specific modules from A-Maze-ing.

## Custom Parameters

The generator accepts custom parameters such as the maze dimensions and
random seed.

For example:

```python
from mazegen import MazeGenerator

generator = MazeGenerator(
    width=20,
    height=15,
    seed=42,
)

maze = generator.generate()
solution = generator.solve()
```

Using the same seed and the same generation parameters produces a deterministic
maze, which is useful for testing and reproducibility.

A random or unspecified seed can be used when a different maze should be
generated on each execution:

```python
from mazegen import MazeGenerator

generator = MazeGenerator(
    width=20,
    height=15,
)

maze = generator.generate()
solution = generator.solve()
```

## Accessing the Generated Structure

The generator exposes the generated maze through its public maze/structure
attribute.

```python
from mazegen import MazeGenerator

generator = MazeGenerator(width=10, height=10, seed=42)

generator.generate()

maze = generator.maze

print(maze)
```

The structure exposed by the reusable module represents the logical maze and
is intended to be consumed directly by another Python program.

The internal representation of the maze does not have to be identical to the
textual representation used by the A-Maze-ing application. This separation
allows future projects to use the generator without depending on the output
format of the original application.

## Accessing the Solution

After generating the maze, the generator can provide a solution path between
the configured entrance and exit.

```python
from mazegen import MazeGenerator

generator = MazeGenerator(
    width=10,
    height=10,
    seed=42,
)

generator.generate()

solution = generator.solve()

for position in solution:
    print(position)
```

The solution is represented as a sequence of maze coordinates, allowing a
calling application to decide how the path should be displayed or processed.

For example, another project could use the solution to:

* display the path in a terminal;
* draw the solution on a graphical interface;
* calculate its length;
* animate a player moving through the maze;
* perform additional pathfinding analysis.

## Reusing the Generator

A future project only needs to import `MazeGenerator` from the package:

```python
from mazegen import MazeGenerator
```

The generator is independent from:

* terminal rendering;
* ANSI colors;
* MiniLibX;
* raycasting;
* `.xpm` textures;
* A-Maze-ing configuration files;
* the project's output files.

This makes `mazegen` suitable as a standalone dependency for another Python
application.

## Minimal Example

The following example shows the complete basic workflow:

```python
from mazegen import MazeGenerator

# Create the generator.
generator = MazeGenerator(
    width=10,
    height=10,
    seed=1234,
)

# Generate the maze.
generator.generate()

# Access the logical maze structure.
maze = generator.maze

# Obtain a solution.
solution = generator.solve()

print("Maze:")
print(maze)

print("Solution:")
print(solution)
```

## Package Development

The package uses Poetry for dependency management and packaging.

Install the project dependencies:

```bash
poetry install
```

Build the package:

```bash
poetry build
```

This creates distributable files in:

```text
dist/
├── mazegen-1.0.0-py3-none-any.whl
└── mazegen-1.0.0.tar.gz
```

The wheel can then be installed into another virtual environment with:

```bash
pip install dist/mazegen-1.0.0-py3-none-any.whl
```

## License

This project, including the reusable `mazegen` package, is licensed under the **GNU General Public License v3.0 (GPL-3.0)**.

The GNU GPLv3 is a free and open-source software license that allows the code to be **used, studied, modified, and redistributed**. Any future project that incorporates or distributes the GPLv3-licensed `mazegen` code must preserve the same freedoms and comply with the terms of the GPLv3.

The complete license text is available in the [`LICENSE.md`](LICENSE.md) file at the root of this repository.

For more information about the GNU GPLv3, visit the official GNU website.
