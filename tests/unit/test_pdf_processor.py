"""Unit tests for PDFProcessor class."""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from pdf_processor.processing.pdf_processor import PDFProcessor, PDFProcessorConfig

class TestPDFProcessor:
    """Test cases for PDFProcessor class."""

    @pytest.fixture
    def sample_config(self, tmp_path):
        """Create a sample configuration for testing."""
        from pdf_processor.processing.image_enhancement import EnhancementStrategy
        return PDFProcessorConfig(
            input_path=str(tmp_path / "input.pdf"),
            output_dir=str(tmp_path / "output"),
            dpi=300,
            max_workers=2,
            timeout=300,
            enhancement_strategies=[
                EnhancementStrategy.ADAPTIVE_THRESHOLD,
                EnhancementStrategy.GRAYSCALE
            ]
        )

    @pytest.fixture
    def mock_processor(self, sample_config):
        """Create a PDFProcessor instance with mock dependencies."""
        with patch('pdf_processor.processing.pdf_processor.ImageEnhancer'), \
             patch('pdf_processor.processing.pdf_processor.OCRProcessor'), \
             patch('pdf_processor.processing.pdf_processor.SVGGenerator'), \
             patch('pdf_processor.processing.pdf_processor.pdf_to_images') as mock_pdf_to_images, \
             patch('pdf_processor.processing.pdf_processor.ensure_directory_exists'):
            
            # Setup mock PDF to return a single page
            mock_pdf_to_images.return_value = ["page1.png"]
            
            processor = PDFProcessor(sample_config)
            
            # Set up mocks for dependencies
            processor.image_enhancer = MagicMock()
            processor.ocr_processor = MagicMock()
            processor.svg_generator = MagicMock()
            
            # Create a mock EnhancementResult
            from pdf_processor.processing.image_enhancement import EnhancementResult, EnhancementStrategy
            mock_enhancement_result = MagicMock()
            mock_enhancement_result.success = True
            mock_enhancement_result.strategy = EnhancementStrategy.ORIGINAL
            mock_enhancement_result.image = MagicMock()
            mock_enhancement_result.parameters = {}
            
            # Mock the enhancement to return a list of EnhancementResult objects
            processor.image_enhancer.enhance_image.return_value = [mock_enhancement_result]
            
            # Mock OCR result
            from pdf_processor.models.ocr_result import OCRResult, TextBlock
            mock_ocr_result = OCRResult(
                text="test text",
                blocks=[TextBlock(text="test", x=0, y=0, width=100, height=100, confidence=0.9)]
            )
            mock_ocr_result.metadata = {}
            processor.ocr_processor.extract_text.return_value = mock_ocr_result
            
            # Mock SVG generation
            processor.svg_generator.generate_svg.return_value = "output_svg_path"
            
            # Mock file operations
            processor._extract_page_as_image = MagicMock(return_value="page_image_path")
            
            return processor

    def test_init(self, sample_config):
        """Test PDFProcessor initialization."""
        processor = PDFProcessor(sample_config)
        assert processor.config == sample_config
        assert processor.logger is not None

    def test_process_pdf_success(self, mock_processor, tmp_path):
        """Test successful PDF processing."""
        # Setup
        input_pdf = tmp_path / "test.pdf"
        # Create a minimal valid PDF file with one page
        pdf_content = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog
   /Pages 2 0 R
>>
endobj
2 0 obj
<< /Type /Pages
   /Kids [3 0 R]
   /Count 1
>>
endobj
3 0 obj
<< /Type /Page
   /Parent 2 0 R
   /Resources << /Font << >> >>
   /MediaBox [0 0 612 792]
   /Contents 4 0 R
>>
endobj
4 0 obj
<< /Length 44 >>
stream
BT
/F1 24 Tf
100 700 Td
(Hello, World!) Tj
ET
endstream
endobj
5 0 obj
<<
  /Type /Font
  /Subtype /Type1
  /BaseFont /Helvetica
>>
endobj
xref
0 6
0000000000 65535 f 
0000000015 00000 n 
0000000069 00000 n 
0000000121 00000 n 
0000000192 00000 n 
0000000242 00000 n 
trailer
<<
  /Size 6
  /Root 1 0 R
  /Info << >>
>>
startxref
320
%%EOF
"""
        input_pdf.write_bytes(pdf_content)
        output_dir = tmp_path / "output"
        
        # Mock the PDF to images conversion
        mock_processor._extract_page_as_image.return_value = "page_image_path"
        
        # Mock the _process_page method
        with patch.object(mock_processor, '_process_page') as mock_process_page:
            mock_process_page.return_value = {
                "text": "test text",
                "blocks": [{"text": "test", "bbox": [0, 0, 100, 100]}],
                "success": True,
                "output_files": []
            }
            
            # Execute with explicit paths
            result = mock_processor.process_pdf(
                pdf_path=str(input_pdf),
                output_dir=str(output_dir)
            )
            
            # Verify
            assert result is not None
            assert len(result) > 0  # Should have processed at least one page
            mock_process_page.assert_called()

    def test_process_page(self, mock_processor, tmp_path):
        """Test processing a single page."""
        # Setup
        test_image = tmp_path / "test.png"
        test_image.write_bytes(b"PNG_HEADER")
        
        # Execute
        result = mock_processor._process_page(
            image_path=str(test_image),
            page_num=1,
            output_dir=str(tmp_path)
        )
        
        # Verify
        assert result["text"] == "test text"
        assert len(result["output_files"]) > 0
        
        # Verify the enhancement was called
        mock_processor.image_enhancer.enhance_image.assert_called_once()
        
        # Verify OCR processing was called
        mock_processor.ocr_processor.extract_text.assert_called_once()
        
        # Verify SVG generation was called
        mock_processor.svg_generator.generate_svg.assert_called_once()

    def test_cleanup_resources(self, mock_processor):
        """Test cleanup of resources."""
        # Execute
        mock_processor.cleanup_resources()
        
        # Verify cleanup was called on dependencies
        mock_processor.image_enhancer.cleanup_resources.assert_called_once()
        mock_processor.ocr_processor.cleanup_resources.assert_called_once()
        mock_processor.svg_generator.cleanup_resources.assert_called_once()
