
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p documents output logs config

# Set environment variables
ENV PYTHONPATH=/app
ENV PDF_OCR_LOG_LEVEL=INFO

# Expose port (if running web service)
EXPOSE 8000

# Default command
CMD ["python", "pdf_processor.py"]
