#!/usr/bin/env python3
"""
PDF OCR Processor - Główny plik

Ten skrypt uruchamia główną funkcjonalność przetwarzania PDF z OCR.

Przykłady użycia:
  # Przetwórz wszystkie PDF-y w domyślnym folderze z domyślnym modelem
  python pdf_processor.py

  # Wskaż konkretny plik i model
  python pdf_processor.py --input dokument.pdf --model llava:7b

  # Przetwórz cały folder
  python pdf_processor.py --input folder_z_pdf --output wyniki

  # Pokaż pomoc
  python pdf_processor.py --help
"""
import argparse
import sys

def parse_arguments():
    parser = argparse.ArgumentParser(description='Przetwarzanie dokumentów PDF z wykorzystaniem OCR')
    parser.add_argument('--input', type=str, help='Ścieżka do pliku PDF lub folderu z plikami PDF')
    parser.add_argument('--output', type=str, help='Folder wyjściowy (domyślnie: output)')
    parser.add_argument('--model', type=str, help='Nazwa modelu do użycia (np. llava:7b)')
    parser.add_argument('--workers', type=int, help='Liczba wątków roboczych')
    parser.add_argument('--verbose', action='store_true', help='Tryb szczegółowy')
    return parser.parse_args()

def main():
    from pdf_processor.processing.pdf_processor import PDFProcessor
    from pdf_processor.cli import main as cli_main
    
    print("🚀 PDF OCR Processor v2.0")
    args = parse_arguments()
    
    # Konfiguracja na podstawie argumentów
    config = {}
    if args.input:
        config['input_path'] = args.input
    if args.output:
        config['output_dir'] = args.output  # Changed from output_folder to output_dir to match PDFProcessorConfig
    if args.model:
        config['ocr_model'] = args.model  # Changed from model to ocr_model to match PDFProcessorConfig
    if args.workers:
        config['max_workers'] = args.workers  # Changed from workers to max_workers to match PDFProcessorConfig
    
    # Create processor with config
    try:
        # Initialize the processor with config
        processor_config = PDFProcessorConfig(**config)
        processor = PDFProcessor(processor_config)
        
        # Check if input is a file or directory
        input_path = Path(config.get('input_path', '.'))
        if input_path.is_file():
            # Process a single file
            print(f"Przetwarzanie pliku: {input_path}")
            result = processor.process_pdf(input_path)
            print(f"Zakończono przetwarzanie. Wynik zapisano w: {result.get('output_path')}")
        else:
            # Process a directory
            print(f"Przetwarzanie plików w katalogu: {input_path}")
            results = processor.process_directory(input_path)
            print(f"Zakończono przetwarzanie {len(results)} plików.")
            
    except KeyboardInterrupt:
        print("\nPrzerwano działanie przez użytkownika.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Wystąpił błąd: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
