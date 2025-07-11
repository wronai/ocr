#!/bin/bash
# Format code

echo "🎨 Formatting code..."
black pdf_processor/ tests/
isort pdf_processor/ tests/
