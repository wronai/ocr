# Scripts Directory

This directory contains bash scripts for various development and build tasks. These scripts are called by the Makefile to perform specific operations.

## Available Scripts

### Installation
- `install.sh` - Install production dependencies
- `install-dev.sh` - Install development dependencies and set up pre-commit hooks

### Testing
- `test.sh` - Run tests
- `test-cov.sh` - Run tests with coverage report
- `verify.sh` - Run verification tests

### Code Quality
- `lint.sh` - Run code linters (flake8, mypy, pylint)
- `format.sh` - Format code using black and isort
- `clean.sh` - Clean up build artifacts and cache files

### Docker
- `docker-build.sh` - Build Docker image
- `docker-run.sh` - Start services with Docker Compose
- `docker-stop.sh` - Stop Docker containers

### Documentation
- `docs.sh` - Build documentation
- `docs-serve.sh` - Serve documentation locally

### Release
- `release.sh` - Create a new release
- `release-upload.sh` - Upload release to PyPI
- `publish.sh` - Full publication process (test, lint, build, and publish)

### Development
- `dev-setup.sh` - Set up development environment
- `dev-server.sh` - Start development server
- `models.sh` - Download required AI models

## Usage

These scripts are designed to be called from the project root using the Makefile. For example:

```bash
# Install dependencies
make install

# Run tests
make test

# Format code
make format

# Build and run with Docker
make docker-build
make docker-run
```

## Adding New Scripts

1. Create a new `.sh` file in this directory
2. Add the shebang line: `#!/bin/bash`
3. Make the script executable: `chmod +x script_name.sh`
4. Add a corresponding target in the main Makefile
5. Update this README to document the new script

## Best Practices

- Keep scripts focused on a single task
- Include error handling
- Use descriptive names
- Document any required environment variables
- Make scripts idempotent when possible
