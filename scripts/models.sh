#!/bin/bash
# Download required models

echo "📥 Downloading models..."
ollama pull llava:7b
ollama pull llama3.2-vision
