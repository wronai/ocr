#!/bin/bash
# Publish package to PyPI

set -e
echo "🚀 Starting publication process..."

# Clean
./scripts/clean.sh

# Run tests
echo -e "\n🔍 Running tests..."
./scripts/test.sh

# Run linters
echo -e "\n🔍 Running linters..."
#./scripts/lint.sh

# Create release
echo -e "\n📦 Creating release..."
#./scripts/release.sh

# Upload to PyPI
echo -e "\n🚀 Uploading to PyPI..."
#./scripts/release-upload.sh
#
#echo -e "\n✅ Successfully published package to PyPI"
