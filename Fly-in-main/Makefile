PYTHON		= python3
VENV		= .venv
SRC_DIR		= src
MAIN		= $(SRC_DIR)/main.py
PIP			= $(VENV)/bin/pip
PYTEST		= $(VENV)/bin/pytest
FLAKE8		= $(VENV)/bin/flake8
MYPY		= $(VENV)/bin/mypy

MAP			?= maps/easy/01_linear_path.txt
 
all: install

$(VENV)/bin/python3:
	@echo ">>> Virtual environment not found."
	@echo ">>> Running installation..."
	@$(MAKE) install
 
install:
	@if [ ! -d "$(VENV)" ]; then \
		echo ">>> Creating virtual environment..."; \
		$(PYTHON) -m venv $(VENV); \
	else \
		echo ">>> Virtual environment already exists."; \
	fi
	@echo ">>> Installing dependencies..."
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo ">>> Installation complete."
 
run: $(VENV)/bin/python3
	@echo ">>> Running Fly-in simulation..."
	PYTHONPATH=. $(VENV)/bin/python3 $(MAIN) $(MAP)

animate: $(VENV)/bin/python3
	@echo ">>> Running Fly-in simulation with animation..."
	PYTHONPATH=. $(VENV)/bin/python3 $(MAIN) $(MAP) --animate
 
debug: $(VENV)/bin/python3
	@echo ">>> Running Fly-in simulation in debug mode..."
	PYTHONPATH=. $(VENV)/bin/python3 -m pdb $(MAIN) $(MAP)

clean:
	@echo ">>> Cleaning temporary files..."
	find . -type d -name "__pycache__"   -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache"   -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc"         -delete 2>/dev/null || true
	find . -type f -name "*.pyo"         -delete 2>/dev/null || true
	@echo ">>> Clean complete."
 
fclean: clean
	@echo ">>> Removing virtual environment..."
	rm -rf $(VENV)
	@echo ">>> Full clean complete."

lint: $(VENV)/bin/python3
	@echo ">>> Running flake8..."
	$(FLAKE8) .
	@echo ">>> Running mypy..."
	$(MYPY) . \
		--warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs
	@echo ">>> Lint complete."
 
lint-strict: $(VENV)/bin/python3
	@echo ">>> Running flake8 (strict)..."
	$(FLAKE8) .
	@echo ">>> Running mypy (strict)..."
	$(MYPY) . --strict
	@echo ">>> Strict lint complete."

help:
	@echo ""
	@echo "  Fly-in — Drone Routing Simulation"
	@echo ""
	@echo "  Targets:"
	@echo "    install      Install project dependencies into a virtual environment"
	@echo "    run          Run the simulation (pass MAP=<map_file> for a specific map)"
	@echo "    animate      Run the simulation with animation (pass MAP=<map_file> for a specific map)"
	@echo "    debug        Run the simulation with Python's pdb debugger"
	@echo "    clean        Remove __pycache__, .mypy_cache, .pytest_cache, *.pyc, *.pyo"
	@echo "    fclean       clean + remove the virtual environment"
	@echo "    lint         Run flake8 + mypy with mandatory flags"
	@echo "    lint-strict  Run flake8 + mypy with --strict"
	@echo ""
	@echo "  Example:"
	@echo "    make run MAP=maps/easy/01_linear_path.txt"
	@echo "    make animate MAP=maps/easy/01_linear_path.txt"
	@echo ""
	@echo "  Virtual Environment:"
	@echo "    To activate the virtual environment, run:"
	@echo "        source $(VENV)/bin/activate"
	@echo ""

.PHONY: all install run animate debug clean fclean lint lint-strict help