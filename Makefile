# SlicerMouseMaster Makefile
# Run common development tasks

.PHONY: help test lint format typecheck docs docs-clean docs-serve all

help:
	@echo "SlicerMouseMaster Development Commands"
	@echo ""
	@echo "  make test        Run unit tests"
	@echo "  make lint        Run linter"
	@echo "  make format      Format code"
	@echo "  make typecheck   Run type checker"
	@echo "  make docs        Build documentation"
	@echo "  make docs-clean  Clean documentation build"
	@echo "  make docs-serve  Build and serve docs locally"
	@echo "  make all         Run lint, typecheck, and test"

# Testing
test:
	uv run pytest MouseMaster/Testing/Python/ -v

test-cov:
	uv run pytest MouseMaster/Testing/Python/ -v --cov=MouseMaster/MouseMasterLib

# Linting and formatting
lint:
	uv run ruff check .

format:
	uv run ruff format .

typecheck:
	uv run mypy MouseMaster/MouseMasterLib/

# Documentation
docs:
	uv run sphinx-build -b html docs docs/_build/html

docs-clean:
	rm -rf docs/_build

docs-serve: docs
	@echo "Documentation built at docs/_build/html/index.html"
	@echo "Starting local server at http://localhost:8000"
	uv run python -m http.server 8000 --directory docs/_build/html

# Combined targets
all: lint typecheck test

check: lint typecheck
