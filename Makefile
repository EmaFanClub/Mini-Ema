.PHONY: style
style:
	@echo "Running Ruff format check..."
	uv run --no-project ruff format --check .
	@echo "Running Ruff linter..."
	uv run --no-project ruff check .

.PHONY: format
format:
	@echo "Running Ruff format..."
	uv run --no-project ruff format .
	@echo "Running Ruff fix..."
	uv run --no-project ruff check --fix .

.PHONY: build
build:
	@echo "Building package..."
	uv build

.PHONY: help
help:
	@echo "Available targets:"
	@echo "  style   - Check code formatting and linting with Ruff"
	@echo "  format  - Auto-format code and fix linting issues with Ruff"
	@echo "  build   - Build the package"
	@echo "  help    - Show this help message"
