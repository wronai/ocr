#!/usr/bin/env python3
"""
Test PDF OCR Processor with various documents
"""
import os
import time
import json
from pathlib import Path
from pdf_processor.pdf_processor import PDFOCRProcessor

def test_pdf_processor(pdf_path, output_dir, test_name):
    """Test the PDF processor with a single PDF file"""
    print(f"\n{'='*50}")
    print(f"TESTING: {test_name}")
    print(f"File: {pdf_path}")
    print(f"{'='*50}")
    
    # Create output directory
    test_output = Path(output_dir) / "test_results" / test_name
    test_output.mkdir(parents=True, exist_ok=True)
    
    # Initialize processor
    processor = PDFOCRProcessor(
        documents_folder=str(Path(pdf_path).parent),
        output_folder=str(test_output)
    )
    
    # Process the PDF and measure time
    start_time = time.time()
    try:
        result = processor.process_pdf(
            str(pdf_path),
            ocr_model="llava:7b",
            parallel_ocr=True
        )
        processing_time = time.time() - start_time
        
        if result and "svg_path" in result:
            print(f"✓ Successfully generated: {result['svg_path']}")
            print(f"✓ Processing time: {processing_time:.2f} seconds")
            
            # Get file sizes
            pdf_size = os.path.getsize(pdf_path) / (1024 * 1024)  # MB
            svg_size = os.path.getsize(result['svg_path']) / (1024 * 1024)  # MB
            print(f"✓ PDF size: {pdf_size:.2f} MB")
            print(f"✓ SVG size: {svg_size:.2f} MB")
            
            # Basic validation
            with open(result['svg_path'], 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"✓ SVG validation: {'Valid' if 'svg' in content[:100].lower() else 'Invalid'}")
                print(f"✓ Text content: {'Found' if 'ocr-text-overlay' in content else 'Not found'}")
            
            return {
                'status': 'success',
                'processing_time': processing_time,
                'pdf_size_mb': pdf_size,
                'svg_size_mb': svg_size,
                'output_path': result['svg_path']
            }
        else:
            print(f"✗ Failed to process: {pdf_path}")
            return {'status': 'failed', 'error': 'No output generated'}
            
    except Exception as e:
        print(f"✗ Error processing {pdf_path}: {str(e)}")
        return {'status': 'error', 'error': str(e)}

def run_tests():
    """Run tests with various PDF documents"""
    test_cases = [
        {
            'path': 'documents/Analiza Rynku Cyfrowych Bliźniaków w Czasie Rzeczy.pdf',
            'name': 'Polish_Text',
            'description': 'Polish language document with text and images'
        },
        # Add more test cases here
    ]
    
    # Look for additional PDFs in the test_documents directory
    test_docs_dir = Path('test_documents')
    if test_docs_dir.exists():
        for i, pdf in enumerate(test_docs_dir.glob('*.pdf')):
            test_cases.append({
                'path': str(pdf),
                'name': f'TestDoc_{i+1}',
                'description': f'Test document {i+1} from test_documents/'
            })
    
    if not test_cases:
        print("No test PDFs found. Please add PDFs to the 'documents' or 'test_documents' directory.")
        return
    
    # Run tests
    results = []
    for test in test_cases:
        if not Path(test['path']).exists():
            print(f"\nSkipping {test['name']} - File not found: {test['path']}")
            continue
            
        result = test_pdf_processor(
            test['path'],
            'output',
            test['name']
        )
        
        if result:
            results.append({
                'test_name': test['name'],
                'file': test['path'],
                'result': result
            })
    
    # Save test results
    results_file = Path('output/test_results.json')
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\nTest results saved to: {results_file}")

if __name__ == "__main__":
    run_tests()
