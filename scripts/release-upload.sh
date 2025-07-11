#!/bin/bash
# Upload release to PyPI

echo "🚀 Uploading to PyPI..."
twine upload dist/*
