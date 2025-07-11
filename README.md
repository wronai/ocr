# PDF OCR Processor

> Advanced PDF processing with AI-powered OCR, text extraction, and selectable text overlays using Ollama models

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](LICENSE)
[![Documentation](https://img.shields.io/badge/Docs-GitHub%20Wiki-blueviolet)](https://github.com/wronai/ocr/wiki)
[![Tests](https://github.com/wronai/ocr/actions/workflows/tests.yml/badge.svg)](https://github.com/wronai/ocr/actions)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## 🚀 Features

- **AI-Powered OCR** using Ollama models (llava, moondream, etc.)
- **Modular Architecture** with clear separation of concerns
- **Multiple Output Formats**:
  - SVG with selectable text overlays
  - Raw text extraction
  - JSON metadata
- **Image Enhancement** with multiple strategies
- **Robust Error Handling** with configurable retries
- **Parallel Processing** for batch operations
- **CLI Interface** with progress tracking

## 🛠️ System Architecture

```
┌─────────────────────────────────────────────────┐
│               PDF OCR Processor                 │
├─────────────────┬───────────────────────────────┤
│  ┌────────────┐ │  ┌─────────────────────────┐  │
│  │ PDF        │ │  │      OCRProcessor       │  │
│  │ Processor  ├─┼─▶│  - Text extraction      │  │
│  └────────────┘ │  │  - Ollama integration   │  │
│                 │  └─────────────┬───────────┘  │
│  ┌────────────┐ │  ┌─────────────▼───────────┐  │
│  │ Image      │ │  │      SVG Generator      │  │
│  │ Enhancer   ├─┼─▶│  - Text overlay         │  │
│  └────────────┘ │  │  - Searchable output    │  │
└─────────────────┴───────────────────────────────┘
```

## 📦 Installation

### Prerequisites
- Python 3.8+
- [Ollama](https://ollama.ai) (for OCR processing)
- System dependencies:
  ```bash
  # Ubuntu/Debian
  sudo apt-get install -y tesseract-ocr poppler-utils
  
  # macOS
  brew install tesseract poppler
  ```

### Install from source
```bash
# Clone the repository
git clone https://github.com/wronai/ocr.git
cd ocr

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development
```

## 🏁 Quick Start

### Basic Usage
```bash
# Process a single PDF
python -m pdf_processor --input document.pdf --output output/

# Process all PDFs in a directory
python -m pdf_processor --input ./documents --output ./output --model llava:7b

# Show help
python -m pdf_processor --help
```

### Python API
```python
from pdf_processor import PDFProcessor
from pdf_processor.processing.pdf_processor import PDFProcessorConfig

# Configure the processor
config = PDFProcessorConfig(
    input_path="document.pdf",
    output_dir="./output",
    ocr_model="llava:7b",
    dpi=300,
    max_workers=4
)

# Process a document
processor = PDFProcessor(config)
result = processor.process_pdf("document.pdf")
print(f"Processed {result['pages_processed']} pages")
```

## ⚙️ Configuration

### Configuration File
Create a `config.yaml` file:

```yaml
# config.yaml
input_path: ./documents    # Input file or directory
output_dir: ./output       # Output directory
ocr_model: llava:7b        # Ollama model to use
dpi: 300                   # Image resolution
max_workers: 4             # Number of worker threads
timeout: 300               # Timeout in seconds
max_retries: 3             # Max retry attempts
log_level: INFO            # Logging level
log_file: pdf_processor.log # Log file path

# Image enhancement strategies
enhancement_strategies:
  - original            # Keep original image
  - grayscale           # Convert to grayscale
  - adaptive_threshold  # Apply adaptive thresholding
  - contrast_stretch    # Stretch contrast
  - sharpen             # Sharpen image
  - denoise             # Remove noise
```

### Environment Variables

```bash
export OLLAMA_HOST="http://localhost:11434"
export OLLAMA_MODEL="llava:7b"
export LOG_LEVEL="DEBUG"
```

## 🚀 Advanced Usage

### Processing Options

```bash
# Process with specific DPI
python -m pdf_processor --input document.pdf --output output/ --dpi 400

# Limit number of pages to process
python -m pdf_processor --input document.pdf --output output/ --max-pages 10

# Use a specific enhancement strategy
python -m pdf_processor --input document.pdf --output output/ --enhance grayscale

# Process in verbose mode
python -m pdf_processor --input document.pdf --output output/ --verbose
```

### Available Enhancement Strategies

- `original`: Keep original image (fastest)
- `grayscale`: Convert to grayscale (good for text-heavy documents)
- `adaptive_threshold`: Apply adaptive thresholding (good for low-quality scans)
- `contrast_stretch`: Stretch contrast to improve readability
- `sharpen`: Apply sharpening filter
- `denoise`: Remove image noise

## 🛠️ Development

### Project Structure

```
pdf_processor/
├── __init__.py          # Package initialization
├── cli.py               # Command-line interface
├── config/              # Configuration files
├── models/              # Data models
│   ├── __init__.py
│   ├── ocr_result.py    # OCR result data structures
│   └── retry_config.py  # Retry configuration
├── processing/          # Core processing modules
│   ├── __init__.py
│   ├── image_enhancement.py  # Image processing
│   ├── ocr_processor.py      # OCR processing
│   ├── pdf_processor.py      # Main PDF processing
│   └── svg_generator.py      # SVG output generation
└── utils/               # Utility functions
    ├── file_utils.py    # File operations
    ├── logging_utils.py # Logging configuration
    └── validation_utils.py # Input validation
```

### Running Tests

```bash
# Install test dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest

# Run tests with coverage report
pytest --cov=pdf_processor --cov-report=html
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 📚 Resources

- [Ollama Documentation](https://ollama.ai/docs)
- [PyMuPDF Documentation](https://pymupdf.readthedocs.io/)
- [Pillow Documentation](https://pillow.readthedocs.io/)

## 🙏 Acknowledgments

- The Ollama team for their amazing AI models
- The PyMuPDF team for excellent PDF processing
- All contributors who have helped improve this project

## 🛠️ Development Workflow

This project uses a script-based workflow for development tasks. All scripts are located in the `scripts/` directory and can be run directly or via the Makefile.

### Setup

1. Clone the repository and navigate to the project directory:
   ```bash
   git clone https://github.com/wronai/ocr.git
   cd ocr
   ```

2. Set up the development environment:
   ```bash
   make install-dev
   ```
   This will:
   - Create and activate a virtual environment
   - Install all development dependencies
   - Set up pre-commit hooks

### Common Development Tasks

```bash
# Run tests
make test

# Run tests with coverage
make test-cov

# Format code
make format

# Run linters
make lint

# Start development server
make dev-server

# Build documentation
make docs
make docs-serve  # Serve docs locally
```

### Scripts Directory

All development and build scripts are located in the `scripts/` directory. See [scripts/README.md](scripts/README.md) for detailed documentation of each script.

### Docker Development

```bash
# Build Docker image
make docker-build

# Start services with Docker Compose
make docker-run

# Stop services
make docker-stop
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please ensure your code follows our coding standards and includes appropriate tests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📜 Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes in each version.**
   ```bash
   python proc.py --model llava:7b --workers 4
   ```

3. **View Results**
   - Open `output/*_complete.svg` in your browser
   - Check details in `output/processing_report.json`

## 📚 Documentation

Full documentation is available in the [docs/](docs/) directory:

- [📖 User Guide](docs/user-guide/README.md)
- [⚙️ Installation and Configuration](docs/getting-started/installation.md)
- [🔧 API Reference](docs/api-reference/README.md)
- [❓ Frequently Asked Questions](docs/faq/README.md)
- [👨‍💻 Development and Contributing](docs/development/contributing.md)
