#!/bin/bash
# Clean build artifacts

echo "🧹 Cleaning up..."
find . -type f -name "*.pyc" -delete
find . -type d -name "__pycache__" -delete
find . -type d -name "*.egg-info" -exec rm -rf {} +
rm -rf build/ dist/ .coverage htmlcov/
