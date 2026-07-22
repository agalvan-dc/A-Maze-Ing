
from pydantic import BaseModel, model_validator, field_validator, Field
from pydantic import ValidationError
import sys


class ValidateConfig(BaseModel):
    width: int = Field(ge=1)
    height: int = Field(ge=1)
    entry: tuple[int, int]
    exit: tuple[int, int]
    output_file: str = Field(min_length=5)
    perfect: bool = Field(default=False)
    seed: int | None

    @field_validator('entry', 'exit', mode='before')
    @classmethod
    def parse_tuple(cls, value: str) -> tuple[int, int] | str:
        if isinstance(value, str):
            try:
                x, y = value.split(',')
                return (int(x.strip()), int(y.strip()))
            except ValueError:
                raise ValueError("Format must be: 'x,y' (ej: '2,3')")
        return value

    @model_validator(mode='after')
    def verify(self) -> 'ValidateConfig':
        entry_x, entry_y = self.entry
        if entry_x >= self.width or entry_y >= self.height:
            raise ValueError(f"Entry point {self.entry} "
                             "outside of maze dimensions "
                             f"({self.width}x{self.height})")

        exit_x, exit_y = self.exit
        if exit_x >= self.width or exit_y >= self.height:
            raise ValueError(f"Exit point {self.exit} outside of maze "
                             f"dimensions ({self.width}x{self.height})")
        if self.entry == self.exit:
            raise ValueError("Entry point and exist point cannot be the same.")

        return self


def validate_conf(filepath: str) -> dict:
    config_dict = {}

    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if not line or '=' not in line:
                    continue

                key, value = line.split('=', 1)
                config_dict[key.strip().lower()] = value.strip()

        config = ValidateConfig(**config_dict)
        return config.model_dump()
    except ValidationError as e:
        print(f"Validation error: {e}")
        sys.exit(1)

def validate_maze(filepath: str, data: dict) -> bool:
    with open(filepath, 'r', encoding='utf-8') as file:
        raw_data = [line.strip() for line in file]
    if data['perfect'] == True:
        

