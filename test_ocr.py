#!/usr/bin/env python3
"""
Test script for PDF OCR Processor
"""
import os
import sys
from pathlib import Path
from pdf_processor.pdf_processor import PDFOCRProcessor

def main():
    # Initialize the processor
    processor = PDFOCRProcessor(
        documents_folder="documents",
        output_folder="output"
    )
    
    # Find PDF files in the documents folder
    pdf_files = list(Path("documents").glob("*.pdf"))
    
    if not pdf_files:
        print("No PDF files found in the documents folder.")
        return
    
    # Process each PDF file
    for pdf_path in pdf_files:
        print(f"Processing: {pdf_path}")
        
        # Process the PDF
        result = processor.process_pdf(
            str(pdf_path),
            ocr_model="llava:7b",
            parallel_ocr=True
        )
        
        if result and "svg_path" in result:
            print(f"✓ Successfully generated: {result['svg_path']}")
        else:
            print(f"✗ Failed to process: {pdf_path}")

if __name__ == "__main__":
    main()
