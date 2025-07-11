#!/bin/bash
# Set up development environment

echo "🚀 Setting up development environment..."
python3 -m pip install -e .
mkdir -p documents output logs config
if [ ! -f config/config.yaml ]; then
    cp config/config.yaml.example config/config.yaml 2>/dev/null || \
    echo "⚠️  Please create config/config.yaml from config/config.yaml.example"
fi
