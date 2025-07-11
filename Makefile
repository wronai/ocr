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
	@echo "  docker-stop  - Stop Docker containers"
	@echo "  docs         - Build documentation"
	@echo "  docs-serve   - Serve documentation locally"
	@echo "  release      - Create release"
	@echo "  release-upload - Upload release to PyPI"
	@echo "  publish      - Build and publish package to PyPI"
	@echo "  dev-setup    - Set up development environment"
	@echo "  dev-server   - Start development server"
	@echo "  setup        - Set up Python virtual environment"
	@echo "  run          - Run the application"
	@echo "  verify       - Run verification tests"
	@echo "  models       - Download required models"

# Installation
install:
	./scripts/install.sh

install-dev:
	./scripts/install-dev.sh

# Testing
test:
	./scripts/test.sh

test-cov:
	./scripts/test-cov.sh

# Code quality
lint:
	./scripts/lint.sh

format:
	./scripts/format.sh

# Cleanup
clean:
	./scripts/clean.sh

# Docker
docker-build:
	./scripts/docker-build.sh

docker-run:
	./scripts/docker-run.sh

docker-stop:
	./scripts/docker-stop.sh

# Documentation
docs:
	./scripts/docs.sh

docs-serve:
	./scripts/docs-serve.sh

# Release
release:
	./scripts/release.sh

release-upload:
	./scripts/release-upload.sh

# Publish package to PyPI
publish:
	./scripts/publish.sh
	poetry version patch
	poetry build
	poetry publish

# Development
dev-setup:
	./scripts/dev-setup.sh

dev-server:
	./scripts/dev-server.sh

# Quick commands
setup:
	python3 -m venv .venv
	. .venv/bin/activate && \
		pip install --upgrade pip && \
		pip install -e .

run:
	./scripts/dev-server.sh

verify:
	./scripts/verify.sh

models:
	./scripts/models.sh


