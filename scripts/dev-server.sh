#!/bin/bash
# Start development server

if [ ! -f .venv/bin/activate ]; then
    echo "❌ Virtual environment not found. Please run 'make setup' first."
    exit 1
fi

echo "🚀 Starting PDF OCR Processor..."
source .venv/bin/activate
python -m pdf_processor
