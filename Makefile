PYTHON == $(shell if [ -x .venv/bin/python3 ]; then echo .venv/bin/python3; else echo python3; fi)

install:
	$(PYTHON) -m pip install flake8 mypy poetry
	poetry install


clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .mypy_cache
	rm -f utilities/maze_output.txt
	rm -f utilities/processed_map.npy

run: 
	poetry run python a_maze_ing.py
lint:
	flake8 .
	$(PYTHON) -m mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 .
	$(PYTHON) -m mypy . --strict

v_env:
	$(PYTHON) -m venv v_env
	$(PYTHON) source v_env/bin/activate  


.PHONY: install run debug clean lint lint-strict v_env
