import sys
from typing import Any

from pydantic import (
    BaseModel, Field, ValidationError, field_validator, model_validator
)


class ValidateConfig(BaseModel):
    """
    Parse and validate the configuration for the maze generator.

    Attributes:
        width: The width of the maze (between 1 and 200).
        height: The height of the maze (between 1 and 200).
        entry: The starting coordinate (x, y).
        exit: The ending coordinate (x, y).
        output_file: The name of the file to save the maze.
        perfect: Whether the maze should be perfect (no loops).
        seed: The random seed for maze generation.
    """

    width: int = Field(ge=1, le=200)
    height: int = Field(ge=1, le=200)
    entry: tuple[int, int]
    exit: tuple[int, int]
    output_file: str = Field(min_length=5)
    perfect: bool = Field(default=False)
    seed: int | None

    @field_validator('entry', 'exit', mode='before')
    @classmethod
    def parse_tuple(cls, value: Any) -> Any:
        """
        Parse a string formatted as 'x,y' into a tuple of integers.
        Args:
            value: The raw value to parse.
        Returns:
            Any: The parsed tuple of integers,
                or the original value if not a string.
        Raises:
            ValueError: If the string format is invalid or cannot be converted.
        """
        if isinstance(value, str):
            try:
                x, y = value.split(',')
                return (int(x.strip()), int(y.strip()))
            except ValueError:
                raise ValueError("Format must be: 'x,y' (ej: '2,3')")
        return value

    @model_validator(mode='after')
    def verify(self) -> 'ValidateConfig':
        """
        Verify that entry and exit points are valid and within bounds.
        Returns:
            ValidateConfig: The validated instance.
        Raises:
            ValueError: If points are out of bounds or identical.
        """
        entry_x, entry_y = self.entry
        if entry_x >= self.width or entry_y >= self.height:
            raise ValueError(
                f"Entry point {self.entry} outside of maze dimensions "
                f"({self.width}x{self.height})"
            )

        exit_x, exit_y = self.exit
        if exit_x >= self.width or exit_y >= self.height:
            raise ValueError(
                f"Exit point {self.exit} outside of maze dimensions "
                f"({self.width}x{self.height})"
            )
        if self.entry == self.exit:
            raise ValueError("Entry point and exit point cannot be the same.")

        return self


def validate_conf(filepath: str) -> dict[str, Any]:
    """Validate the configuration file and return its values.
        Args:
            filepath: Path to the configuration file.
        Returns:
            dict[str, Any]: A dictionary containing the
            validated configuration.
    """
    config_dict: dict[str, Any] = {}

    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if '=' not in line:
                    raise SyntaxError("Invalid line format: missing '='")

                key, value = line.split('=', 1)
                clean_key = key.strip().lower()

                if clean_key in config_dict:
                    raise SyntaxError("Repeated parameters")

                config_dict[clean_key] = value.strip()

        config = ValidateConfig(**config_dict)
        return config.model_dump()
    except ValidationError as e:
        error_msg = e.errors()[0]['msg']
        print("Expected validation error:")
        print(error_msg)
        sys.exit(1)
