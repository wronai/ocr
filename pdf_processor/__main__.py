#!/usr/bin/env python3
"""
PDF OCR Processor - Command Line Interface

This module provides the command line interface for the PDF OCR Processor.
"""
import sys
import os
from .pdf_processor import main, PDFOCRProcessor

def cli():
    """Command line interface entry point"""
    # Default configuration
    config = {
        'input_dir': 'documents',
        'output_dir': 'output',
        'model': 'llava:7b',
        'workers': 4,
        'show_ocr_highlights': True,
        'translate_to_polish': True
    }
    
    # Parse command line arguments
    if '--help' in sys.argv or '-h' in sys.argv:
        print("""PDF OCR Processor
        
Usage:
  python -m pdf_processor [options]

Options:
  --input-dir DIR     Input directory with PDF files (default: documents)
  --output-dir DIR    Output directory (default: output)
  --model MODEL       OCR model to use (default: llava:7b)
  --workers N         Number of parallel workers (default: 4)
  --no-highlights     Disable OCR highlights
  --no-translate      Disable translation to Polish
  -h, --help          Show this help message
        """)
        return 0
    
    # Update config from command line
    args = iter(sys.argv[1:])
    for arg in args:
        if arg == '--input-dir':
            config['input_dir'] = next(args, 'documents')
        elif arg == '--output-dir':
            config['output_dir'] = next(args, 'output')
        elif arg == '--model':
            config['model'] = next(args, 'llava:7b')
        elif arg == '--workers':
            config['workers'] = int(next(args, '4'))
        elif arg == '--no-highlights':
            config['show_ocr_highlights'] = False
        elif arg == '--no-translate':
            config['translate_to_polish'] = False
    
    # Create output directory if it doesn't exist
    os.makedirs(config['output_dir'], exist_ok=True)
    
    # Run the processor
    processor = PDFOCRProcessor(
        documents_folder=config['input_dir'],
        output_folder=config['output_dir']
    )
    
    # Set additional options
    processor.show_ocr_highlights = config['show_ocr_highlights']
    processor.translate_to_polish = config['translate_to_polish']
    
    return processor.process_all_pdfs(
        ocr_model=config['model'],
        parallel_ocr=(config['workers'] > 1)
    )

if __name__ == "__main__":
    sys.exit(cli())
