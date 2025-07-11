#!/bin/bash
# Run tests

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

echo "🚀 Running tests..."
python -m pytest tests/ -v
