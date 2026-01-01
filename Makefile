.PHONY: style
style:
	@echo "Running Ruff format check..."
	uvx ruff format --check .
	@echo "Running Ruff linter..."
	uvx ruff check .

.PHONY: format
format:
	@echo "Running Ruff format..."
	uvx ruff format .
	@echo "Running Ruff fix..."
	uvx ruff check --fix .

.PHONY: build
build:
	@echo "Building package..."
	uv build

.PHONY: test
test:
	@echo "Running tests..."
	@for test_file in tests/test_*.py; do \
		echo "Running $$test_file..."; \
		uv run python $$test_file || exit 1; \
	done
	@echo "All tests passed!"

.PHONY: help
help:
	@echo "Available targets:"
	@echo "  style   - Check code formatting and linting with Ruff"
	@echo "  format  - Auto-format code and fix linting issues with Ruff"
	@echo "  build   - Build the package"
	@echo "  test    - Run tests"
	@echo "  help    - Show this help message"
