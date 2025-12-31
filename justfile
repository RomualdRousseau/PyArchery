set dotenv-load

APP_NAME := "pyarchery"
ARCHERY_VERSION := "1.0.46"

# Default recipe to display help
default:
    @just --list

# Install dependencies
install:
    uv sync

# Install development dependencies
install-dev:
    uv sync --dev

# Update all dependencies
update:
    uv sync --upgrade

# Run the application
run *args:
    uv run python examples/{{args}}

# Run tests
test:
    uv run python -m pytest

# Run tests with coverage
test-cov:
    uv run python -m pytest --cov=src --cov-report=html --cov-report=term

# Run profiling
profile:
    uv run python -m cProfile -o {{APP_NAME}}.prof -m {{APP_NAME}}
    uvx snakeviz {{APP_NAME}}.prof

# Run linting
lint:
    uvx ruff check .
    uvx ty check .

# Format code
format:
    uvx ruff format .
    uvx ruff check --fix .

# Run security checks
security:
    uvx bandit -r src/

# Clean build artifacts and cache
clean:
    uvx pyclean . --debris
    rm -rf src/pyarchery.jars

# Build the package
build:
    uv build

# Install the package in development mode
dev-install:
    uv pip install -e .

# Run pre-commit hooks
pre-commit:
    uvx pre-commit run --all-files

# Initialize pre-commit
init-pre-commit:
    uvx pre-commit install

# Enter the virtual environment shell
shell:
    uv run python

# Show project info
info:
    uv version
    @echo ""
    @echo "Python version:"
    uv run python --version

# Export requirements.txt for compatibility
export-requirements:
    uv export --format requirements-txt --output-file requirements.txt

# Lock dependencies
lock:
    uv lock

# Start editing
edit:
    uv run nvim .

# Build documentation
doc-build:
    uv run mkdocs build

# Deploy documentation
doc-deploy:
    uv run mkdocs gh-deploy

# Deploy to PyPi
deploy:
  uvx twine upload dist/*

generate-deps-step1:
  rm -f src/pyarchery/dependencies.sha256
  echo '__version__ = "{{ARCHERY_VERSION}}"' > src/pyarchery/version.py
  cat ../Archery/dependencies.txt | sed -E 's/1.0-SNAPSHOT/{{ARCHERY_VERSION}}/' > src/pyarchery/dependencies

generate-deps-step2:
  bash generate_checksums.sh
