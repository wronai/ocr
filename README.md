# PDF OCR Processor

> Advanced PDF processing with AI-powered OCR, text extraction, and selectable text overlays

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Documentation](https://img.shields.io/badge/Docs-Read%20the%20Docs-blueviolet)](https://pdf-ocr-processor.readthedocs.io/)
[![PyPI](https://img.shields.io/pypi/v/pdf-ocr-processor)](https://pypi.org/project/pdf-ocr-processor/)
[![Tests](https://github.com/wronai/ocr/actions/workflows/tests.yml/badge.svg)](https://github.com/wronai/ocr/actions)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## 🚀 Features

- **AI-Powered OCR** using Ollama models (llava, moondream, etc.)
- **Modular Architecture** for easy extension and customization
- **Multiple Output Formats**:
  - SVG with selectable text overlays
  - Searchable PDFs
  - Raw text and JSON exports
- **Image Enhancement** with multiple strategies
- **Robust Error Handling** with retry mechanisms
- **Parallel Processing** for batch operations
- **Interactive CLI** with progress tracking
- **Web Interface** (optional)

## 📦 Installation

### Prerequisites
- Python 3.8+
- [Ollama](https://ollama.ai) (for OCR processing)
- System dependencies (see [Installation Guide](docs/getting-started/installation.md))

### Install from PyPI (recommended)
```bash
pip install pdf-ocr-processor[gpu]  # For GPU acceleration
# or
pip install pdf-ocr-processor  # CPU-only
```

### Install from source
```bash
# Clone the repository
git clone https://github.com/wronai/ocr.git
cd ocr

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
.\venv\Scripts\activate  # Windows

# Install in development mode with all optional dependencies
pip install -e ".[dev,gpu,web]"
```

## 🏁 Quick Start

### Basic Usage
```bash
# Process a single PDF
pdf-ocr process document.pdf --output output/

# Process all PDFs in a directory
pdf-ocr batch ./documents --output ./output --model llava:7b

# Start the web interface
pdf-ocr-web
```

### Python API
```python
from pdf_processor import PDFProcessor
from pdf_processor.config import PDFProcessorConfig

# Configure the processor
config = PDFProcessorConfig(
    output_dir="./output",
    ocr_model="llava:7b",
    languages=["en", "pl"],
    enable_image_enhancement=True,
    max_workers=4
)

# Process a document
processor = PDFProcessor(config)
result = processor.process_pdf("document.pdf")
print(f"Processed {result['page_count']} pages")
```

### Configuration

You can configure the processor using a YAML file:

```yaml
# config.yaml
output_dir: ./output
ocr_model: llava:7b
languages: [en, pl]
enable_image_enhancement: true
max_workers: 4
image_dpi: 300
```

Then use it like this:
```bash
pdf-ocr process document.pdf --config config.yaml
```

## 📚 Documentation

For detailed documentation, including API reference and advanced usage, please visit:

📖 [PDF OCR Processor Documentation](https://pdf-ocr-processor.readthedocs.io/)

## 🛠️ Development

### Running Tests
```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Run with coverage report
pytest --cov=pdf_processor tests/
```

### Code Style
This project uses:
- [Black](https://github.com/psf/black) for code formatting
- [isort](https://github.com/PyCQA/isort) for import sorting
- [mypy](https://mypy-lang.org/) for static type checking

Run the following to format and check the code:
```bash
black .
isort .
mypy .
```

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) to get started.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📜 Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes in each version.**
   ```bash
   python proc.py --model llava:7b --workers 4
   ```

3. **Zobacz wyniki**
   - Otwórz plik `output/*_complete.svg` w przeglądarce
   - Sprawdź szczegóły w `output/processing_report.json`

## 📚 Dokumentacja

Pełna dokumentacja dostępna w katalogu [docs/](docs/):

- [📖 Przewodnik użytkownika](docs/user-guide/README.md)
- [⚙️ Instalacja i konfiguracja](docs/getting-started/installation.md)
- [🔧 Referencja API](docs/api-reference/README.md)
- [❓ Często zadawane pytania](docs/faq/README.md)
- [👨‍💻 Rozwój i współtworzenie](docs/development/contributing.md)

## 📝 Licencja

Ten projekt jest dostępny na licencji MIT. Zobacz plik [LICENSE](LICENSE) aby uzyskać więcej informacji.

## 🤝 Współtworzenie

Wkład jest mile widziany! Zobacz [przewodnik współtworzenia](docs/development/contributing.md) aby dowiedzieć się więcej o tym, jak możesz pomóc w rozwoju projektu.
