PYTHON  = python3
VENV    = .venv
SRC_DIR = src
MAIN    = $(SRC_DIR)/main.py
PIP     = $(VENV)/bin/pip
PYTEST  = $(VENV)/bin/pytest
FLAKE8  = $(VENV)/bin/flake8
MYPY    = $(VENV)/bin/mypy

MAP     ?= maps/easy/03_basic_capacity.txt

all: install

$(VENV)/bin/python3:
	@$(MAKE) install

install:
	@test -d $(VENV) || $(PYTHON) -m venv $(VENV)
	@$(PIP) install --upgrade pip -q
	@$(PIP) install -r requirements.txt -q

run: $(VENV)/bin/python3
	@PYTHONPATH=. $(VENV)/bin/python3 $(MAIN) $(MAP)

debug: $(VENV)/bin/python3
	@PYTHONPATH=. $(VENV)/bin/python3 -m pdb $(MAIN) $(MAP)

clean:
	@find . -type d \( -name "__pycache__" -o -name ".mypy_cache" \
		-o -name ".pytest_cache" \) -exec rm -rf {} + 2>/dev/null || true
	@find . -type f \( -name "*.pyc" -o -name "*.pyo" \) -delete

fclean: clean
	@rm -rf $(VENV)

lint: $(VENV)/bin/python3
	@$(FLAKE8) .
	@$(MYPY) . \
		--warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs

lint-strict: $(VENV)/bin/python3
	@$(FLAKE8) .
	@$(MYPY) . --strict

.PHONY: all install run debug clean fclean lint lint-strict