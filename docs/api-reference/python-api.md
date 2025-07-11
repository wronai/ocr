# Python API Reference

This document provides detailed documentation for the Python API of the OCR system.

## Table of Contents

1. [PDFOCRProcessor](#pdfocrprocessor)
2. [Configuration](#configuration)
3. [OCR Processing](#ocr-processing)
4. [Translation](#translation)
5. [SVG Generation](#svg-generation)
6. [Utilities](#utilities)

## PDFOCRProcessor

The main class for processing PDF documents with OCR capabilities.

### Initialization

```python
from pdf_processor import PDFOCRProcessor

# Basic initialization
processor = PDFOCRProcessor(
    output_folder="output",
    temp_folder="temp",
    log_level="INFO"
)

# With translation enabled
translator = PDFOCRProcessor(
    output_folder="output",
    translate_to_polish=True,
    display_mode="grid"  # or "scroll"
)
```

### Configuration Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `output_folder` | str | "output" | Directory to save processed files |
| `temp_folder` | str | "temp" | Directory for temporary files |
| `log_level` | str | "INFO" | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `translate_to_polish` | bool | False | Enable translation to Polish |
| `display_mode` | str | "scroll" | Display mode ("scroll" or "grid") |
| `show_ocr_highlights` | bool | True | Show OCR highlight overlays |
| `dpi` | int | 200 | DPI for image conversion |
| `model` | str | "llava:7b" | Ollama model to use for OCR |

## OCR Processing

### Process a Single PDF

```python
# Process a PDF file
result = processor.process_pdf(
    "documents/sample.pdf",
    output_svg="output/result.svg"
)

# Result contains processing information
print(f"Processed {result['page_count']} pages")
print(f"Output saved to: {result['output_svg']}")
```

### Process Multiple PDFs

```python
# Process all PDFs in a directory
results = processor.process_directory(
    "documents/",
    output_dir="output/"
)

for result in results:
    print(f"Processed: {result['input']}")
    print(f"Output: {result['output_svg']}")
```

## Translation

### Enable Translation

```python
# Create processor with translation enabled
translator = PDFOCRProcessor(
    translate_to_polish=True,
    output_folder="output"
)

# Process document with translation
result = translator.process_pdf("document_en.pdf")
```

### Custom Translation Function

You can provide a custom translation function:

```python
def my_translator(text, source_lang, target_lang):
    # Implement your translation logic here
    return f"[TRANSLATED to {target_lang}] {text}"

processor = PDFOCRProcessor(
    translate_to_polish=True,
    translation_func=my_translator
)
```

## SVG Generation

### Generate SVG with OCR Data

```python
# Generate SVG with OCR metadata
svg_content = processor.create_optimized_svg(
    pdf_path="document.pdf",
    image_paths=["page1.png", "page2.png"],
    ocr_results=[ocr_page1, ocr_page2]
)

# Save to file
with open("output/document.svg", "w") as f:
    f.write(svg_content)
```

### Customizing SVG Output

```python
# Customize SVG generation
class CustomSVGGenerator(PDFOCRProcessor):
    def _add_document_metadata(self, svg_root, pdf_path, page_count):
        # Custom metadata implementation
        metadata = ET.SubElement(svg_root, "metadata")
        doc_info = ET.SubElement(metadata, "document")
        doc_info.set("title", Path(pdf_path).name)
        doc_info.set("pages", str(page_count))
        doc_info.set("created", datetime.now().isoformat())
```

## Utilities

### Extract Text from PDF

```python
# Extract text from a single page
with open("page1_ocr.json") as f:
    ocr_data = json.load(f)

text = processor.extract_text(ocr_data)
print(text)
```

### Get Page Images

```python
# Convert PDF to images
images = processor.pdf_to_images("document.pdf", dpi=300)
for i, img_path in enumerate(images):
    print(f"Page {i+1}: {img_path}")
```

## Error Handling

```pythontry:
    result = processor.process_pdf("invalid.pdf")
except FileNotFoundError as e:
    print(f"File not found: {e}")
except Exception as e:
    print(f"Processing failed: {e}")
```

## Examples

### Process PDF with Custom Settings

```python
processor = PDFOCRProcessor(
    output_folder="results",
    dpi=300,
    model="llama3.2-vision",
    translate_to_polish=True,
    show_ocr_highlights=False
)

result = processor.process_pdf(
    "important_document.pdf",
    output_svg="results/document_with_translation.svg"
)
```

### Batch Processing with Progress

```python
from tqdm import tqdm

pdf_files = [f for f in Path("documents").glob("*.pdf")]

for pdf_file in tqdm(pdf_files, desc="Processing PDFs"):
    try:
        processor.process_pdf(
            str(pdf_file),
            output_svg=f"output/{pdf_file.stem}.svg"
        )
    except Exception as e:
        print(f"Failed to process {pdf_file}: {e}")
```

## Advanced Usage

### Custom OCR Processing

```python
def custom_ocr_processing(image_path):
    # Implement custom OCR processing
    return {
        "text": "Extracted text",
        "blocks": [
            {
                "text": "Extracted text",
                "bbox": [0, 0, 100, 100],
                "confidence": 0.95
            }
        ]
    }

# Use custom OCR function
processor = PDFOCRProcessor()
result = processor.process_pdf(
    "document.pdf",
    ocr_processor=custom_ocr_processing
)
```

### Extending the Processor

```python
class CustomOCRProcessor(PDFOCRProcessor):
    def __init__(self, custom_param=None, **kwargs):
        super().__init__(**kwargs)
        self.custom_param = custom_param
    
    def _process_page(self, image_path, page_num):
        # Custom page processing
        result = super()._process_page(image_path, page_num)
        # Add custom processing
        result["custom_data"] = self.custom_param
        return result
```

## Troubleshooting

### Common Issues

1. **Missing Dependencies**
   - Ensure all system dependencies are installed
   - Check `requirements.txt` for Python dependencies

2. **OCR Quality**
   - Increase DPI for better quality
   - Try a different OCR model
   - Pre-process images if needed

3. **Translation Issues**
   - Check internet connection if using online translation
   - Verify language codes are correct
   - Implement rate limiting if needed

## Support

For issues and feature requests, please open an issue on our [GitHub repository](https://github.com/wronai/ocr).
