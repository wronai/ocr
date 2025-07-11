"""Command-line interface for PDF OCR Processor."""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

from .models.retry_config import RetryConfig
from .processing.image_enhancement import EnhancementStrategy
from .processing.pdf_processor import PDFProcessor, PDFProcessorConfig


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command line arguments.
    
    Args:
        args: List of command line arguments. If None, uses sys.argv[1:]
        
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Extract text from PDFs using OCR and generate searchable output.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Required arguments
    parser.add_argument(
        'input_path',
        type=str,
        help="Path to a PDF file or directory containing PDFs"
    )
    
    # Output options
    parser.add_argument(
        '-o', '--output-dir',
        type=str,
        default="./output",
        help="Output directory for processed files"
    )
    
    # Processing options
    processing = parser.add_argument_group('Processing Options')
    processing.add_argument(
        '--model',
        type=str,
        default="llava:7b",
        help="OCR model to use (e.g., 'llava:7b')"
    )
    processing.add_argument(
        '--language',
        type=str,
        default="polish",
        help="Language for OCR (e.g., 'english', 'polish')"
    )
    processing.add_argument(
        '--dpi',
        type=int,
        default=300,
        help="DPI for PDF to image conversion"
    )
    processing.add_argument(
        '--workers',
        type=int,
        default=4,
        help="Maximum number of worker threads"
    )
    processing.add_argument(
        '--timeout',
        type=int,
        default=300,
        help="Timeout in seconds for OCR operations"
    )
    processing.add_argument(
        '--max-retries',
        type=int,
        default=3,
        help="Maximum number of retries for failed operations"
    )
    
    # Image enhancement options
    enhancement = parser.add_argument_group('Image Enhancement Options')
    enhancement.add_argument(
        '--no-enhancement',
        action='store_true',
        help="Disable all image enhancement"
    )
    enhancement.add_argument(
        '--strategy',
        action='append',
        choices=[s.name.lower() for s in EnhancementStrategy],
        help="Image enhancement strategies to apply (can be used multiple times)"
    )
    
    # Output format options
    output = parser.add_argument_group('Output Options')
    output.add_argument(
        '--no-images',
        action='store_true',
        help="Don't save enhanced images"
    )
    output.add_argument(
        '--no-svg',
        action='store_true',
        help="Don't generate SVG output"
    )
    output.add_argument(
        '--no-text',
        action='store_true',
        help="Don't save text output"
    )
    
    # Logging options
    logging_group = parser.add_argument_group('Logging Options')
    logging_group.add_argument(
        '-v', '--verbose',
        action='store_true',
        help="Enable verbose output"
    )
    logging_group.add_argument(
        '--log-file',
        type=str,
        help="Log file path"
    )
    logging_group.add_argument(
        '--quiet',
        action='store_true',
        help="Suppress all output except errors"
    )
    
    # Parse arguments
    return parser.parse_args(args)


def setup_logging(verbose: bool = False, log_file: Optional[str] = None, quiet: bool = False) -> None:
    """Configure logging.
    
    Args:
        verbose: Enable verbose logging
        log_file: Path to log file
        quiet: Suppress all output except errors
    """
    log_level = logging.DEBUG if verbose else (
        logging.ERROR if quiet else logging.INFO
    )
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(log_level)
    
    # Clear any existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(log_level)
    
    # Create formatter and add it to the handlers
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    
    # Add the handlers to the logger
    logger.addHandler(console_handler)
    
    # Add file handler if log file is specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)


def get_enhancement_strategies(args: argparse.Namespace) -> List[EnhancementStrategy]:
    """Get the list of enhancement strategies to use.
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        List of enhancement strategies
    """
    if args.no_enhancement:
        return [EnhancementStrategy.ORIGINAL]
    
    if args.strategy:
        strategies = []
        for name in args.strategy:
            try:
                strategies.append(EnhancementStrategy[name.upper()])
            except KeyError:
                print(f"Warning: Unknown enhancement strategy: {name}", file=sys.stderr)
        return strategies if strategies else [EnhancementStrategy.ORIGINAL]
    
    # Default strategies
    return [
        EnhancementStrategy.ORIGINAL,
        EnhancementStrategy.GRAYSCALE,
        EnhancementStrategy.ADAPTIVE_THRESHOLD,
    ]


def main(args: Optional[List[str]] = None) -> int:
    """Main entry point for the CLI.
    
    Args:
        args: Command line arguments. If None, uses sys.argv[1:]
        
    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    # Parse command line arguments
    args = parse_args(args)
    
    # Set up logging
    setup_logging(
        verbose=args.verbose,
        log_file=args.log_file,
        quiet=args.quiet
    )
    
    logger = logging.getLogger(__name__)
    
    try:
        # Create output directory if it doesn't exist
        output_dir = Path(args.output_dir).resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Get enhancement strategies
        strategies = get_enhancement_strategies(args)
        
        # Create processor configuration
        config = PDFProcessorConfig(
            input_path=args.input_path,
            output_dir=output_dir,
            ocr_model=args.model,
            language=args.language,
            dpi=args.dpi,
            max_workers=args.workers,
            timeout=args.timeout,
            max_retries=args.max_retries,
            enhancement_strategies=strategies,
            save_images=not args.no_images,
            save_svg=not args.no_svg,
            save_text=not args.no_text,
            log_level=logging.DEBUG if args.verbose else (
                logging.ERROR if args.quiet else logging.INFO
            ),
            log_file=args.log_file
        )
        
        # Initialize processor
        processor = PDFProcessor(config)
        
        # Check if input is a file or directory
        input_path = Path(args.input_path).resolve()
        
        if input_path.is_file():
            # Process single file
            logger.info(f"Processing file: {input_path}")
            result = processor.process_pdf(input_path)
            
            # Print result summary
            print("\nProcessing complete!")
            print(f"Input: {input_path}")
            print(f"Output directory: {result.get('output_dir')}")
            print(f"Pages processed: {result.get('pages_processed', 0)}/{result.get('total_pages', 0)}")
            
            if result['status'] == 'completed':
                return 0
            else:
                print(f"Error: {result.get('error', 'Unknown error')}", file=sys.stderr)
                return 1
                
        elif input_path.is_dir():
            # Process directory
            logger.info(f"Processing directory: {input_path}")
            results = processor.process_directory()
            
            # Print summary
            total = len(results)
            successful = sum(1 for r in results if r.get('status') == 'completed')
            failed = total - successful
            
            print("\nBatch processing complete!")
            print(f"Total files: {total}")
            print(f"Successful: {successful}")
            print(f"Failed: {failed}")
            
            # Save results to a JSON file
            results_file = output_dir / "processing_results.json"
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'timestamp': str(datetime.now().isoformat()),
                    'input_path': str(input_path),
                    'output_dir': str(output_dir),
                    'results': results
                }, f, indent=2, ensure_ascii=False)
            
            print(f"\nDetailed results saved to: {results_file}")
            
            return 0 if failed == 0 else 1
            
        else:
            print(f"Error: Input path does not exist: {input_path}", file=sys.stderr)
            return 1
            
    except Exception as e:
        logger.exception("An unexpected error occurred")
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
