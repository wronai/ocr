# PDF OCR Processor - Development Makefile

.PHONY: help install install-dev test lint format clean docker-build docker-run docs publish

# Default target
help:
	@echo "PDF OCR Processor - Available commands:"
	@echo ""
	@echo "  install      - Install production dependencies"
	@echo "  install-dev  - Install development dependencies"
	@echo "  test         - Run tests"
	@echo "  test-cov     - Run tests with coverage"
	@echo "  lint         - Run linting"
	@echo "  format       - Format code"
	@echo "  clean        - Clean build artifacts"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-run   - Run with Docker Compose"
	@echo "  docs         - Build documentation"
	@echo "  release      - Create release"
	@echo "  release-upload - Upload release to PyPI"
	@echo "  publish      - Build and publish package to PyPI"

# Installation
install:
	python3 -m pip install -r requirements.txt

install-dev:
	python3 -m pip install -r requirements-dev.txt
	pre-commit install

# Testing
.PHONY: test test-cov

test:
	@echo "🚀 Running tests..."
	python3 -m pytest tests/ -v

test-cov:
	@echo "📊 Running tests with coverage..."
	python3 -m pytest tests/ -v

# Code quality
lint:
	flake8 pdf_processor/ tests/
	mypy pdf_processor/
	pylint pdf_processor/

format:
	black pdf_processor/ tests/
	isort pdf_processor/ tests/

# Cleanup
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/ dist/ .coverage htmlcov/

# Docker
docker-build:
	docker build -t pdf-ocr-processor .

docker-run:
	docker-compose up -d

docker-stop:
	docker-compose down

# Documentation
docs:
	cd docs && make html

docs-serve:
	cd docs/_build/html && python -m http.server 8080

# Release
release: clean test lint
	python setup.py sdist bdist_wheel
	twine check dist/*

release-upload:
	twine upload dist/*

# Publish package to PyPI
publish:
	@echo "🚀 Starting publication process..."
	$(MAKE) clean
	@echo "\n🔍 Running tests..."
	$(MAKE) test
	@echo "\n🔍 Running linters..."
	$(MAKE) lint
	@echo "\n📦 Creating release..."
	$(MAKE) release
	@echo "\n🚀 Uploading to PyPI..."
	$(MAKE) release-upload
	@echo "\n✅ Successfully published package to PyPI"


# Development
dev-setup: install-dev
	mkdir -p documents output logs config
	cp config/config.yaml.example config/config.yaml

dev-server:
	python -m pdf_processor.web

# Quick commands
setup:
	@echo "Setting up development environment..."
	python3 -m venv .venv
	. .venv/bin/activate && \
		pip install --upgrade pip && \
		pip install -e .

run:
	@if [ ! -f .venv/bin/activate ]; then \
		echo "❌ Virtual environment not found. Please run 'make setup' first."; \
		exit 1; \
	fi
	@echo "🚀 Starting PDF OCR Processor..."
	. .venv/bin/activate && python -m pdf_processor

verify:
	python3 test_runner.py --verify

models:
	ollama pull llava:7b
	ollama pull llama3.2-vision


