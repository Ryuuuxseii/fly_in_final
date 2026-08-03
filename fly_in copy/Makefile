PYTHON		= python3
VENV		= .venv
SRC_DIR		= src
MAIN		= $(SRC_DIR)/main.py
PIP			= $(VENV)/bin/pip
PYTEST		= $(VENV)/bin/pytest
FLAKE8		= $(VENV)/bin/flake8
MYPY		= $(VENV)/bin/mypy

MAP			?= maps/easy/03_basic_capacity.txt
 
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

debug: $(VENV)/bin/python3
	@echo ">>> Running Fly-in simulation in debug mode..."
	PYTHONPATH=. $(VENV)/bin/python3 -m pdb $(MAIN) $(MAP)

clean:
	find . -type d -name "__pycache__"   -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache"   -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc"         -delete 2>/dev/null || true
	find . -type f -name "*.pyo"         -delete 2>/dev/null || true
	@echo "--->> Clean complete."
 
fclean: clean
	@echo "--->> Removing virtual environment..."
	rm -rf $(VENV)

lint: $(VENV)/bin/python3
	$(FLAKE8) .
	$(MYPY) . \
		--warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs
	@echo "--->> Lint complete."
 
lint-strict: $(VENV)/bin/python3
	$(FLAKE8) .
	$(MYPY) . --strict


.PHONY: all install run debug clean fclean lint lint-strict help