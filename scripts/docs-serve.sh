#!/bin/bash
# Serve documentation locally

echo "🌐 Serving documentation on http://localhost:8080"
cd docs/_build/html && python -m http.server 8080
