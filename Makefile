.PHONY: clean install test lint

# Remove build artifacts and caches
clean:
	rm -rf env __pycache__ *.egg-info build dist

# Create a fresh virtual environment and install dependencies
install:
	python3.11 -m venv env
	./env/bin/pip install --upgrade pip setuptools wheel
	./env/bin/pip install -r requirements.txt -r requirements-dev.txt

# Run tests using pytest
test:
	./env/bin/pytest

# Run linters and formatters
lint:
	./env/bin/flake8 .
	./env/bin/black --check .
	./env/bin/isort --check-only .
