#!/bin/bash
# Run tests with coverage

echo "📊 Running tests with coverage..."
python3 -m pytest tests/ -v --cov=pdf_processor --cov-report=term-missing --cov-report=html
