PYTHON = python3

install:
	$(PYTHON) -m pip install flake8 mypy poetry
	poetry install


clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .mypy_cache
	rm -rf dist
	rm -f utilities/maze_output.txt
	rm -f utilities/processed_map.npy
	rm -f poetry.lock

run: 
	poetry run python a_maze_ing.py

debug:
	poetry run python -m pdb a_maze_ing.py

lint:
	flake8 . --exclude=mlx,venv
	$(PYTHON) -m mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs --exclude='^(mlx|venv)(/|$$)'

lint-strict:
	flake8 . --exclude=mlx,venv
	$(PYTHON) -m mypy --strict --exclude='^(mlx|venv)(/|$$)' .

v_env:
	$(PYTHON) -m venv venv 


.PHONY: install run debug clean lint lint-strict v_env
