#!/bin/bash
# Create release

set -e
echo "📦 Creating release..."
python setup.py sdist bdist_wheel
twine check dist/*
