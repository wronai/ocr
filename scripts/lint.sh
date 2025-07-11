#!/bin/bash
# Run code quality checks

echo "🔍 Running code quality checks..."
flake8 pdf_processor/ tests/
mypy pdf_processor/
pylint pdf_processor/
