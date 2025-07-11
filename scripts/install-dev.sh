#!/bin/bash
# Install development dependencies

echo "🔧 Installing development dependencies..."
python3 -m pip install -r requirements-dev.txt
pre-commit install
