PYTHON == $(shell if [ -x .venv/bin/python3 ]; then echo .venv/bin/python3; else echo python3; fi)
CONFIG == config.txt

install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install flake8 mypy
	$(PYTHON) -m pip install -r utilities/requirements.txt


clean:

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