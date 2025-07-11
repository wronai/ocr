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
    from pdf_processor import PDFOCRProcessor, main as processor_main
    
    print("🚀 PDF OCR Processor v2.0")
    args = parse_arguments()
    
    # Konfiguracja na podstawie argumentów
    config = {}
    if args.input:
        config['input_path'] = args.input
    if args.output:
        config['output_folder'] = args.output
    if args.model:
        config['model'] = args.model
    if args.workers:
        config['workers'] = args.workers
    
    # Uruchom główną funkcję z modułu
    try:
        processor_main(config=config)
    except KeyboardInterrupt:
        print("\nPrzerwano działanie przez użytkownika.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Wystąpił błąd: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
