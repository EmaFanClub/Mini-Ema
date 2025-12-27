.PHONY: style
style:
	@echo "Running Ruff format check..."
	ruff format --check .
	@echo "Running Ruff linter..."
	ruff check .

.PHONY: format
format:
	@echo "Running Ruff format..."
	ruff format .
	@echo "Running Ruff fix..."
	ruff check --fix .

.PHONY: help
help:
	@echo "Available targets:"
	@echo "  style   - Check code formatting and linting with Ruff"
	@echo "  format  - Auto-format code and fix linting issues with Ruff"
	@echo "  help    - Show this help message"
