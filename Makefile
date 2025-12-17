.PHONY: test unit_test perf_test coverage lint doc clean

# Variables
PYTHON := python3
PYTEST := pytest
COVERAGE := coverage
RUFF := ruff
PDOC := pdoc3

# Tests
test:
	$(PYTEST) tests/ -v

unit_test:
	$(PYTEST) -m "not performance" tests/ -v

perf_test:
	$(PYTEST) -m performance tests/ -v

# Couverture
coverage:
	$(COVERAGE) run -m pytest tests/
	$(COVERAGE) report
	$(COVERAGE) html
	@echo "Rapport HTML généré dans htmlcov/index.html"

# Qualité
lint:
	$(RUFF) check .
lint-fix:
	$(RUFF) check --fix .


# Documentation
doc:
	$(PDOC) --html --output-dir docs triangulator --force
	@echo "Documentation générée dans docs/"

# Nettoyage
clean:
	rm -rf __pycache__ .pytest_cache .coverage htmlcov docs
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} +