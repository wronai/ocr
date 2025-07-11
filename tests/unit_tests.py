# tests/unit/test_pdf_processor.py
"""
Testy jednostkowe dla klasy PDFOCRProcessor
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile

# Załóżmy że główny kod jest w pdf_processor.py
# from pdf_processor import PDFOCRProcessor


class TestPDFOCRProcessorInit:
    """Testy inicjalizacji PDFOCRProcessor"""
    
    def test_init_with_default_folders(self, mock_processor_dirs):
        """Test inicjalizacji z domyślnymi folderami"""
        # Mockuj klasę - zastąp rzeczywistym importem
        # processor = PDFOCRProcessor()
        # assert processor.documents_folder.name == "documents"
        # assert processor.output_folder.name == "output"
        pass  # Placeholder - zastąp rzeczywistym testem
    
    def test_init_with_custom_folders(self, mock_processor_dirs):
        """Test inicjalizacji z customowymi folderami"""
        # processor = PDFOCRProcessor(
        #     documents_folder=mock_processor_dirs["documents"],
        #     output_folder=mock_processor_dirs["output"]
        # )
        # assert str(processor.documents_folder) == mock_processor_dirs["documents"]
        pass  # Placeholder
    
    def test_output_folder_creation(self, temp_dir):
        """Test czy output folder jest tworzony automatycznie"""
        output_path = temp_dir / "new_output"
        assert not output_path.exists()
        
        # processor = PDFOCRProcessor(output_folder=str(output_path))
        # assert output_path.exists()
        pass  # Placeholder


class TestOllamaIntegration:
    """Testy integracji z Ollama"""
    
    @patch('subprocess.run')
    def test_check_ollama_success(self, mock_run):
        """Test sprawdzenia Ollama - sukces"""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="NAME\t\tID\t\tSIZE\t\tMODIFIED\nllava:7b\t123\t4.1GB\t2 hours ago"
        )
        
        # processor = PDFOCRProcessor()
        # models = processor.check_ollama_and_models()
        # assert "llava:7b" in models
        
        mock_run.assert_called_once_with(
            ['ollama', 'list'], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
    
    @patch('subprocess.run')
    def test_check_ollama_not_installed(self, mock_run):
        """Test gdy Ollama nie jest zainstalowana"""
        mock_run.side_effect = FileNotFoundError("ollama command not found")
        
        # with pytest.raises(Exception, match="Ollama nie jest zainstalowana"):
        #     processor = PDFOCRProcessor()
        pass  # Placeholder
    
    @patch('subprocess.run')
    def test_check_ollama_timeout(self, mock_run):
        """Test timeout przy sprawdzaniu Ollama"""
        import subprocess
        mock_run.side_effect = subprocess.TimeoutExpired('ollama', 10)
        
        # with pytest.raises(Exception, match="Ollama nie odpowiada"):
        #     processor = PDFOCRProcessor()
        pass  # Placeholder
    
    def test_validate_model_existing(self):
        """Test walidacji istniejącego modelu"""
        # processor = PDFOCRProcessor()
        # processor.available_models = ["llava:7b", "llama3.2-vision"]
        # assert processor.validate_model("llava:7b") == True
        pass  # Placeholder
    
    def test_validate_model_nonexistent(self):
        """Test walidacji nieistniejącego modelu"""
        # processor = PDFOCRProcessor()
        # processor.available_models = ["llava:7b"]
        # assert processor.validate_model("nonexistent:model") == False
        pass  # Placeholder


class TestOCRFunctionality:
    """Testy funkcjonalności OCR"""
    
    @patch('subprocess.run')
    @patch('builtins.open', create=True)
    def test_extract_text_success(self, mock_open, mock_run, mock_ollama_response):
        """Test udanego wyodrębniania tekstu"""
        mock_open.return_value.__enter__.return_value.read.return_value = b'fake_image_data'
        mock_run.return_value = Mock(
            returncode=0,
            stdout=json.dumps(mock_ollama_response).encode()
        )
        
        # processor = PDFOCRProcessor()
        # processor.available_models = ["llava:7b"]
        # result = processor.extract_text_with_ollama("fake_image.png", "llava:7b")
        
        # assert result["text"] == "Sample extracted text from PDF"
        # assert result["confidence"] == 0.95
        # assert result["language"] == "en"
        pass  # Placeholder
    
    @patch('subprocess.run')
    def test_extract_text_ollama_error(self, mock_run):
        """Test błędu Ollama podczas OCR"""
        mock_run.return_value = Mock(
            returncode=1,
            stderr=b"Model not found"
        )
        
        # processor = PDFOCRProcessor()
        # result = processor.extract_text_with_ollama("fake_image.png", "nonexistent:model")
        
        # assert result["text"] == ""
        # assert result["confidence"] == 0.0
        # assert "error" in result
        pass  # Placeholder
    
    def test_extract_text_invalid_image_path(self):
        """Test OCR z niepoprawną ścieżką obrazu"""
        # processor = PDFOCRProcessor()
        # result = processor.extract_text_with_ollama("/nonexistent/image.png", "llava:7b")
        
        # assert result["text"] == ""
        # assert "error" in result
        # assert "Plik nie istnieje" in result["error"]
        pass  # Placeholder
    
    @patch('subprocess.run')
    def test_extract_text_timeout(self, mock_run):
        """Test timeout podczas OCR"""
        import subprocess
        mock_run.side_effect = subprocess.TimeoutExpired('ollama', 300)
        
        # processor = PDFOCRProcessor()
        # result = processor.extract_text_with_ollama("image.png", "llava:7b")
        
        # assert result["text"] == ""
        # assert "Timeout" in result["error"]
        pass  # Placeholder
    
    def test_validate_ocr_result_valid(self, mock_ollama_response):
        """Test walidacji poprawnego wyniku OCR"""
        # processor = PDFOCRProcessor()
        # validated = processor._validate_ocr_result(mock_ollama_response)
        
        # assert validated["text"] == mock_ollama_response["text"]
        # assert validated["confidence"] == mock_ollama_response["confidence"]
        # assert len(validated["blocks"]) == 1
        pass  # Placeholder
    
    def test_validate_ocr_result_invalid(self):
        """Test walidacji niepoprawnego wyniku OCR"""
        invalid_result = {
            "text": 123,  # Powinien być string
            "confidence": "high",  # Powinien być float
            "blocks": "not a list"  # Powinno być listą
        }
        
        # processor = PDFOCRProcessor()
        # validated = processor._validate_ocr_result(invalid_result)
        
        # assert isinstance(validated["text"], str)
        # assert isinstance(validated["confidence"], float)
        # assert isinstance(validated["blocks"], list)
        pass  # Placeholder


class TestPDFProcessing:
    """Testy przetwarzania plików PDF"""
    
    @patch('fitz.open')
    def test_pdf_to_images_success(self, mock_fitz_open, sample_pdf_file):
        """Test udanej konwersji PDF na obrazy"""
        # Mock PyMuPDF
        mock_doc = Mock()
        mock_doc.__len__ = Mock(return_value=2)  # 2 strony
        mock_page = Mock()
        mock_pixmap = Mock()
        
        mock_fitz_open.return_value = mock_doc
        mock_doc.load_page.return_value = mock_page
        mock_page.get_pixmap.return_value = mock_pixmap
        
        # processor = PDFOCRProcessor()
        # image_paths = processor.pdf_to_images(sample_pdf_file)
        
        # assert len(image_paths) == 2
        # assert mock_doc.load_page.call_count == 2
        # assert mock_pixmap.save.call_count == 2
        pass  # Placeholder
    
    @patch('fitz.open')
    def test_pdf_to_images_file_not_found(self, mock_fitz_open):
        """Test konwersji nieistniejącego pliku PDF"""
        mock_fitz_open.side_effect = FileNotFoundError("File not found")
        
        # processor = PDFOCRProcessor()
        # image_paths = processor.pdf_to_images("/nonexistent/file.pdf")
        
        # assert image_paths == []
        pass  # Placeholder
    
    @patch('fitz.open')
    def test_pdf_to_images_corrupted_pdf(self, mock_fitz_open):
        """Test konwersji uszkodzonego PDF"""
        mock_fitz_open.side_effect = Exception("PDF corrupted")
        
        # processor = PDFOCRProcessor()
        # image_paths = processor.pdf_to_images("corrupted.pdf")
        
        # assert image_paths == []
        pass  # Placeholder
    
    @patch('PIL.Image.open')
    def test_resize_image_if_needed_large(self, mock_image_open):
        """Test zmniejszania dużego obrazu"""
        mock_img = Mock()
        mock_img.size = (3000, 2000)  # Większy niż max_image_size
        mock_image_open.return_value.__enter__.return_value = mock_img
        
        # processor = PDFOCRProcessor()
        # processor.max_image_size = (2048, 2048)
        # result_path = processor.resize_image_if_needed("large_image.png")
        
        # assert result_path.endswith(".resized.png")
        # mock_img.thumbnail.assert_called_once()
        pass  # Placeholder
    
    @patch('PIL.Image.open') 
    def test_resize_image_if_needed_small(self, mock_image_open):
        """Test obrazu który nie wymaga zmniejszenia"""
        mock_img = Mock()
        mock_img.size = (800, 600)  # Mniejszy niż max_image_size
        mock_image_open.return_value.__enter__.return_value = mock_img
        
        # processor = PDFOCRProcessor()
        # processor.max_image_size = (2048, 2048)
        # result_path = processor.resize_image_if_needed("small_image.png")
        
        # assert result_path == "small_image.png"
        # mock_img.thumbnail.assert_not_called()
        pass  # Placeholder


class TestSVGGeneration:
    """Testy generowania plików SVG"""
    
    @patch('PIL.Image.open')
    @patch('builtins.open', create=True)
    def test_create_optimized_svg_success(self, mock_file_open, mock_image_open):
        """Test udanego tworzenia SVG"""
        # Mock image dimensions
        mock_img = Mock()
        mock_img.size = (800, 600)
        mock_image_open.return_value.__enter__.return_value = mock_img
        
        # Mock file operations
        mock_file_open.return_value.__enter__.return_value.read.return_value = b'fake_image_data'
        
        # processor = PDFOCRProcessor()
        # svg_path = processor.create_optimized_svg(
        #     "test.pdf",
        #     ["page1.png", "page2.png"],
        #     [mock_ollama_response, mock_ollama_response]
        # )
        
        # assert svg_path.endswith("_complete.svg")
        pass  # Placeholder
    
    def test_add_document_metadata(self):
        """Test dodawania metadanych dokumentu"""
        import xml.etree.ElementTree as ET
        
        svg_root = ET.Element("svg")
        
        # processor = PDFOCRProcessor()
        # processor._add_document_metadata(svg_root, "test.pdf", 5)
        
        # metadata = svg_root.find("metadata")
        # assert metadata is not None
        # doc_info = metadata.find("document-info")
        # assert doc_info.get("pages") == "5"
        pass  # Placeholder
    
    def test_save_svg_with_formatting(self, temp_dir):
        """Test zapisywania SVG z formatowaniem"""
        import xml.etree.ElementTree as ET
        
        svg_root = ET.Element("svg", {"width": "100", "height": "100"})
        svg_path = temp_dir / "test.svg"
        
        # processor = PDFOCRProcessor()
        # processor._save_svg_with_formatting(svg_root, svg_path)
        
        # assert svg_path.exists()
        # content = svg_path.read_text()
        # assert '<?xml version="1.0" encoding="UTF-8"?>' in content
        # assert '<svg' in content
        pass  # Placeholder


class TestBatchProcessing:
    """Testy przetwarzania wielu plików"""
    
    def test_process_all_pdfs_no_files(self, mock_processor_dirs):
        """Test gdy brak plików PDF do przetworzenia"""
        # processor = PDFOCRProcessor(
        #     documents_folder=mock_processor_dirs["documents"]
        # )
        # results = processor.process_all_pdfs()
        
        # assert results == []
        pass  # Placeholder
    
    def test_process_all_pdfs_with_files(self, mock_processor_dirs, sample_pdf_content):
        """Test przetwarzania wielu plików PDF"""
        docs_dir = Path(mock_processor_dirs["documents"])
        
        # Utwórz testowe pliki PDF
        (docs_dir / "test1.pdf").write_bytes(sample_pdf_content)
        (docs_dir / "test2.pdf").write_bytes(sample_pdf_content)
        
        # processor = PDFOCRProcessor(
        #     documents_folder=str(docs_dir)
        # )
        
        # with patch.object(processor, 'process_pdf') as mock_process:
        #     mock_process.return_value = {"page_count": 1, "processing_time": 1.0}
        #     results = processor.process_all_pdfs()
        
        # assert len(results) == 2
        # assert mock_process.call_count == 2
        pass  # Placeholder
    
    @patch('concurrent.futures.ThreadPoolExecutor')
    def test_process_ocr_parallel(self, mock_executor):
        """Test równoległego przetwarzania OCR"""
        mock_future = Mock()
        mock_future.result.return_value = {"text": "test", "confidence": 0.9}
        mock_executor.return_value.__enter__.return_value.submit.return_value = mock_future
        
        # processor = PDFOCRProcessor()
        # results = processor.process_ocr_parallel(
        #     ["image1.png", "image2.png"],
        #     "llava:7b"
        # )
        
        # assert len(results) == 2
        pass  # Placeholder


class TestReportGeneration:
    """Testy generowania raportów"""
    
    def test_generate_detailed_report(self, temp_dir):
        """Test generowania szczegółowego raportu"""
        test_results = [
            {
                "pdf_path": "test1.pdf",
                "page_count": 2,
                "processing_time": 10.5,
                "average_confidence": 0.95,
                "svg_path": "test1_complete.svg"
            },
            {
                "pdf_path": "test2.pdf", 
                "error": "Processing failed"
            }
        ]
        
        # processor = PDFOCRProcessor(output_folder=str(temp_dir))
        # report_path = processor.generate_detailed_report(test_results)
        
        # assert Path(report_path).exists()
        # with open(report_path, 'r') as f:
        #     report = json.load(f)
        
        # assert report["statistics"]["successful_files"] == 1
        # assert report["statistics"]["failed_files"] == 1
        # assert report["statistics"]["total_pages"] == 2
        pass  # Placeholder


class TestConfigurationAndSettings:
    """Testy konfiguracji i ustawień"""
    
    def test_default_settings(self):
        """Test domyślnych ustawień"""
        # processor = PDFOCRProcessor()
        # assert processor.max_workers == 4
        # assert processor.timeout == 300
        # assert processor.max_image_size == (2048, 2048)
        pass  # Placeholder
    
    def test_custom_settings(self):
        """Test customowych ustawień"""
        # processor = PDFOCRProcessor()
        # processor.max_workers = 8
        # processor.timeout = 600
        # processor.max_image_size = (1024, 1024)
        
        # assert processor.max_workers == 8
        # assert processor.timeout == 600
        # assert processor.max_image_size == (1024, 1024)
        pass  # Placeholder


class TestErrorHandling:
    """Testy obsługi błędów"""
    
    def test_empty_ocr_result(self):
        """Test tworzenia pustego wyniku OCR"""
        # processor = PDFOCRProcessor()
        # result = processor._empty_ocr_result("Test error")
        
        # assert result["text"] == ""
        # assert result["confidence"] == 0.0
        # assert result["language"] == "unknown"
        # assert result["blocks"] == []
        # assert result["error"] == "Test error"
        pass  # Placeholder
    
    def test_cleanup_temp_files(self, temp_dir):
        """Test czyszczenia plików tymczasowych"""
        # Utwórz pliki .resized.png
        (temp_dir / "test.resized.png").touch()
        (temp_dir / "other.resized.png").touch()
        (temp_dir / "normal.png").touch()  # Nie powinien być usunięty
        
        # processor = PDFOCRProcessor(output_folder=str(temp_dir))
        # processor.cleanup_temp_files()
        
        # assert not (temp_dir / "test.resized.png").exists()
        # assert not (temp_dir / "other.resized.png").exists()
        # assert (temp_dir / "normal.png").exists()
        pass  # Placeholder


# Parametryzowane testy
class TestParametrized:
    """Testy parametryzowane dla różnych scenariuszy"""
    
    @pytest.mark.parametrize("model,expected_valid", [
        ("llava:7b", True),
        ("llama3.2-vision", True), 
        ("nonexistent:model", False),
        ("", False),
        (None, False),
    ])
    def test_model_validation_parametrized(self, model, expected_valid):
        """Test walidacji różnych modeli"""
        # processor = PDFOCRProcessor()
        # processor.available_models = ["llava:7b", "llama3.2-vision"]
        # assert processor.validate_model(model) == expected_valid
        pass  # Placeholder
    
    @pytest.mark.parametrize("dpi,expected_size", [
        (150, "smaller"),
        (200, "medium"),
        (300, "larger"),
    ])
    def test_dpi_impact_on_image_size(self, dpi, expected_size):
        """Test wpływu DPI na rozmiar obrazów"""
        # processor = PDFOCRProcessor()
        # # Test logiki związanej z DPI
        pass  # Placeholder
    
    @pytest.mark.parametrize("worker_count,expected_performance", [
        (1, "slow"),
        (4, "balanced"),
        (8, "fast"),
    ])
    def test_worker_count_performance(self, worker_count, expected_performance):
        """Test wpływu liczby workerów na wydajność"""
        # processor = PDFOCRProcessor()
        # processor.max_workers = worker_count
        # # Test logiki wydajności
        pass  # Placeholder


# Markery testów
@pytest.mark.unit
class TestUnitMarked:
    """Testy oznaczone jako unit tests"""
    
    def test_simple_unit(self):
        """Prosty test jednostkowy"""
        assert 1 + 1 == 2
    
    def test_string_operations(self):
        """Test operacji na stringach"""
        text = "Hello World"
        assert text.lower() == "hello world"
        assert text.replace("World", "Python") == "Hello Python"


@pytest.mark.slow  
class TestSlowMarked:
    """Testy oznaczone jako wolne"""
    
    def test_slow_operation(self):
        """Test wolnej operacji"""
        import time
        start = time.time()
        time.sleep(0.1)  # Symulacja wolnej operacji
        end = time.time()
        assert end - start >= 0.1


@pytest.mark.integration
class TestIntegrationMarked:
    """Testy integracyjne"""
    
    @pytest.mark.skipif(not Path("documents").exists(), 
                       reason="Wymaga folderu documents")
    def test_integration_with_real_files(self):
        """Test integracyjny z prawdziwymi plikami"""
        # Test wymaga prawdziwego środowiska
        pass


# Test fixtures w akcji
class TestFixtureUsage:
    """Przykłady użycia fixtures"""
    
    def test_with_temp_dir(self, temp_dir):
        """Test używający temporary directory fixture"""
        test_file = temp_dir / "test.txt"
        test_file.write_text("Hello World")
        
        assert test_file.exists()
        assert test_file.read_text() == "Hello World"
    
    def test_with_sample_pdf(self, sample_pdf_file):
        """Test używający sample PDF fixture"""
        assert Path(sample_pdf_file).exists()
        assert Path(sample_pdf_file).suffix == ".pdf"
    
    def test_with_mock_response(self, mock_ollama_response):
        """Test używający mock Ollama response"""
        assert mock_ollama_response["confidence"] == 0.95
        assert "text" in mock_ollama_response
        assert len(mock_ollama_response["blocks"]) == 1


# Helper functions dla testów
def create_test_pdf_with_text(output_path: str, text: str = "Test content"):
    """Helper do tworzenia testowego PDF z tekstem"""
    # W prawdziwej implementacji użyłbyś biblioteki do generowania PDF
    # Na potrzeby testów, prosty mock
    with open(output_path, 'wb') as f:
        f.write(b'%PDF-1.4\n% Fake PDF with text: ' + text.encode() + b'\n%%EOF')

def assert_valid_svg(svg_path: str):
    """Helper do sprawdzania poprawności SVG"""
    import xml.etree.ElementTree as ET
    
    try:
        tree = ET.parse(svg_path)
        root = tree.getroot()
        assert root.tag.endswith('svg')
        return True
    except ET.ParseError:
        return False

def assert_ocr_result_structure(result: dict):
    """Helper do sprawdzania struktury wyniku OCR"""
    required_keys = ["text", "confidence", "language", "blocks"]
    for key in required_keys:
        assert key in result, f"Missing key: {key}"
    
    assert isinstance(result["text"], str)
    assert isinstance(result["confidence"], (int, float))
    assert 0 <= result["confidence"] <= 1
    assert isinstance(result["language"], str)
    assert isinstance(result["blocks"], list)

# tests/integration/test_end_to_end.py
"""
Testy end-to-end dla PDF OCR Processor
"""

import pytest
import tempfile
from pathlib import Path
import json
import xml.etree.ElementTree as ET

# Wymaga zainstalowanego Ollama i modeli
pytestmark = pytest.mark.integration


class TestEndToEndProcessing:
    """Testy pełnego pipeline'u przetwarzania"""
    
    @pytest.mark.slow
    def test_complete_workflow_single_pdf(self, sample_pdf_file):
        """Test kompletnego workflow dla pojedynczego PDF"""
        pytest.importorskip("fitz", reason="PyMuPDF required")
        
        # Ten test wymaga prawdziwego środowiska z Ollama
        # from pdf_processor import PDFOCRProcessor
        
        # with tempfile.TemporaryDirectory() as tmp_dir:
        #     processor = PDFOCRProcessor(output_folder=tmp_dir)
        #     
        #     # Test czy Ollama jest dostępna
        #     try:
        #         models = processor.check_ollama_and_models()
        #         if not models:
        #             pytest.skip("Brak dostępnych modeli Ollama")
        #     except Exception:
        #         pytest.skip("Ollama niedostępna")
        #     
        #     # Przetwórz PDF
        #     result = processor.process_pdf(sample_pdf_file, models[0])
        #     
        #     # Sprawdź wyniki
        #     assert "error" not in result
        #     assert result["page_count"] > 0
        #     assert result["processing_time"] > 0
        #     assert 0 <= result["average_confidence"] <= 1
        #     
        #     # Sprawdź czy pliki zostały utworzone
        #     assert len(result["image_paths"]) == result["page_count"]
        #     for image_path in result["image_paths"]:
        #         assert Path(image_path).exists()
        pass  # Placeholder
    
    @pytest.mark.slow
    def test_batch_processing_workflow(self):
        """Test workflow dla wielu plików"""
        # from pdf_processor import PDFOCRProcessor
        
        # with tempfile.TemporaryDirectory() as tmp_dir:
        #     documents_dir = Path(tmp_dir) / "documents"
        #     output_dir = Path(tmp_dir) / "output"
        #     documents_dir.mkdir()
        #     
        #     # Utwórz kilka testowych PDFów
        #     for i in range(3):
        #         pdf_path = documents_dir / f"test_{i}.pdf"
        #         create_test_pdf_with_text(str(pdf_path), f"Content {i}")
        #     
        #     processor = PDFOCRProcessor(
        #         documents_folder=str(documents_dir),
        #         output_folder=str(output_dir)
        #     )
        #     
        #     # Przetwórz wszystkie
        #     results = processor.process_all_pdfs()
        #     
        #     # Sprawdź wyniki
        #     assert len(results) == 3
        #     successful = [r for r in results if "error" not in r]
        #     assert len(successful) > 0
        #     
        #     # Sprawdź raport
        #     report_path = processor.generate_detailed_report(results)
        #     assert Path(report_path).exists()
        #     
        #     with open(report_path, 'r') as f:
        #         report = json.load(f)
        #     
        #     assert report["statistics"]["total_documents"] == 3
        pass  # Placeholder
    
    def test_svg_generation_and_validation(self, sample_pdf_file):
        """Test generowania i walidacji plików SVG"""
        # from pdf_processor import PDFOCRProcessor
        
        # with tempfile.TemporaryDirectory() as tmp_dir:
        #     processor = PDFOCRProcessor(output_folder=tmp_dir)
        #     
        #     # Symuluj wyniki OCR
        #     mock_ocr_results = [
        #         {
        #             "text": "Page 1 content",
        #             "confidence": 0.9,
        #             "language": "en",
        #             "blocks": []
        #         }
        #     ]
        #     
        #     # Stwórz mockowe obrazy
        #     from PIL import Image
        #     img_path = Path(tmp_dir) / "page_001.png"
        #     img = Image.new('RGB', (800, 600), color='white')
        #     img.save(img_path)
        #     
        #     # Generuj SVG
        #     svg_path = processor.create_optimized_svg(
        #         sample_pdf_file,
        #         [str(img_path)],
        #         mock_ocr_results
        #     )
        #     
        #     # Waliduj SVG
        #     assert Path(svg_path).exists()
        #     assert assert_valid_svg(svg_path)
        #     
        #     # Sprawdź zawartość SVG
        #     tree = ET.parse(svg_path)
        #     root = tree.getroot()
        #     
        #     # Sprawdź metadane
        #     metadata = root.find('.//{http://www.w3.org/2000/svg}metadata')
        #     assert metadata is not None
        #     
        #     # Sprawdź embedded images
        #     images = root.findall('.//{http://www.w3.org/2000/svg}image')
        #     assert len(images) > 0
        #     
        #     # Sprawdź searchable text
        #     texts = root.findall('.//{http://www.w3.org/2000/svg}text')
        #     assert len(texts) > 0
        pass  # Placeholder


class TestPerformanceIntegration:
    """Testy wydajności w środowisku integracyjnym"""
    
    @pytest.mark.slow
    def test_memory_usage_large_document(self):
        """Test zużycia pamięci przy dużym dokumencie"""
        pytest.importorskip("psutil", reason="psutil required for memory monitoring")
        
        # import psutil
        # from pdf_processor import PDFOCRProcessor
        
        # process = psutil.Process()
        # initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # # Symuluj duży dokument (wiele stron)
        # with tempfile.TemporaryDirectory() as tmp_dir:
        #     processor = PDFOCRProcessor(output_folder=tmp_dir)
        #     
        #     # Test z ograniczeniem pamięci
        #     processor.max_image_size = (1024, 1024)  # Mniejsze obrazy
        #     processor.max_workers = 2  # Mniej workerów
        #     
        #     # Symuluj przetwarzanie
        #     # ... kod przetwarzania ...
        #     
        #     final_memory = process.memory_info().rss / 1024 / 1024  # MB
        #     memory_increase = final_memory - initial_memory
        #     
        #     # Sprawdź czy przyrost pamięci jest rozsądny (< 500MB)
        #     assert memory_increase < 500
        pass  # Placeholder
    
    @pytest.mark.slow
    def test_processing_time_benchmarks(self):
        """Test benchmarków czasu przetwarzania"""
        import time
        # from pdf_processor import PDFOCRProcessor
        
        # with tempfile.TemporaryDirectory() as tmp_dir:
        #     processor = PDFOCRProcessor(output_folder=tmp_dir)
        #     
        #     # Test różnych konfiguracji
        #     configs = [
        #         {"workers": 1, "dpi": 150, "model": "llava:7b"},
        #         {"workers": 4, "dpi": 200, "model": "llava:7b"},
        #         {"workers": 2, "dpi": 300, "model": "llama3.2-vision"},
        #     ]
        #     
        #     results = {}
        #     
        #     for config in configs:
        #         processor.max_workers = config["workers"]
        #         
        #         start_time = time.time()
        #         # ... symulacja przetwarzania ...
        #         end_time = time.time()
        #         
        #         results[f"config_{config['workers']}w_{config['dpi']}dpi"] = {
        #             "time": end_time - start_time,
        #             "config": config
        #         }
        #     
        #     # Sprawdź czy więcej workerów = szybsze przetwarzanie
        #     # (dla tego samego DPI i modelu)
        #     # assert results["config_4w_200dpi"]["time"] < results["config_1w_200dpi"]["time"]
        pass  # Placeholder


class TestErrorRecoveryIntegration:
    """Testy odzyskiwania po błędach w środowisku integracyjnym"""
    
    def test_recovery_after_ollama_restart(self):
        """Test odzyskiwania po restarcie Ollama"""
        # from pdf_processor import PDFOCRProcessor
        
        # processor = PDFOCRProcessor()
        
        # # Symuluj restart Ollama podczas przetwarzania
        # # (trudne do testowania bez prawdziwego środowiska)
        pass  # Placeholder
    
    def test_partial_processing_recovery(self):
        """Test odzyskiwania po częściowym przetworzeniu"""
        # Test scenariusza gdy część plików zostanie przetworzona
        # a część nie (np. przez błąd lub przerwanie)
        pass  # Placeholder
    
    def test_corrupted_file_handling(self):
        """Test obsługi uszkodzonych plików"""
        # from pdf_processor import PDFOCRProcessor
        
        # with tempfile.TemporaryDirectory() as tmp_dir:
        #     documents_dir = Path(tmp_dir) / "documents"
        #     documents_dir.mkdir()
        #     
        #     # Utwórz poprawny PDF
        #     good_pdf = documents_dir / "good.pdf"
        #     create_test_pdf_with_text(str(good_pdf), "Good content")
        #     
        #     # Utwórz uszkodzony "PDF"
        #     bad_pdf = documents_dir / "bad.pdf"
        #     bad_pdf.write_bytes(b"This is not a PDF file")
        #     
        #     processor = PDFOCRProcessor(documents_folder=str(documents_dir))
        #     results = processor.process_all_pdfs()
        #     
        #     # Sprawdź czy jeden sukces, jeden błąd
        #     successful = [r for r in results if "error" not in r]
        #     failed = [r for r in results if "error" in r]
        #     
        #     assert len(successful) == 1
        #     assert len(failed) == 1
        #     assert "good.pdf" in successful[0]["pdf_path"]
        #     assert "bad.pdf" in failed[0]["pdf_path"]
        pass  # Placeholder


class TestConfigurationIntegration:
    """Testy integracji z konfiguracją"""
    
    def test_yaml_config_loading(self):
        """Test ładowania konfiguracji z pliku YAML"""
        import yaml
        
        config_content = """
        processing:
          max_workers: 8
          timeout_seconds: 600
          default_dpi: 300
        
        ollama:
          preferred_models:
            - "llama3.2-vision"
            - "llava:7b"
          host: "localhost:11434"
        
        output:
          create_svg: true
          embed_images: false
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(config_content)
            config_path = f.name
        
        try:
            # from pdf_processor import PDFOCRProcessor
            
            # processor = PDFOCRProcessor(config_file=config_path)
            
            # assert processor.max_workers == 8
            # assert processor.timeout == 600
            # assert "llama3.2-vision" in processor.preferred_models
            
            pass  # Placeholder
        finally:
            Path(config_path).unlink()
    
    def test_environment_variables_override(self):
        """Test przesłaniania konfiguracji zmiennymi środowiskowymi"""
        import os
        
        # Ustaw zmienne środowiskowe
        os.environ["PDF_OCR_MAX_WORKERS"] = "16"
        os.environ["PDF_OCR_TIMEOUT"] = "900"
        
        try:
            # from pdf_processor import PDFOCRProcessor
            
            # processor = PDFOCRProcessor()
            
            # assert processor.max_workers == 16
            # assert processor.timeout == 900
            
            pass  # Placeholder
        finally:
            # Wyczyść zmienne środowiskowe
            os.environ.pop("PDF_OCR_MAX_WORKERS", None)
            os.environ.pop("PDF_OCR_TIMEOUT", None)


# Pomocnicze funkcje dla testów integracyjnych
def wait_for_ollama_ready(timeout=30):
    """Czeka aż Ollama będzie gotowa"""
    import time
    import subprocess
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            result = subprocess.run(['ollama', 'list'], 
                                  capture_output=True, timeout=5)
            if result.returncode == 0:
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        time.sleep(1)
    return False

def ensure_test_model_available(model_name="llava:7b"):
    """Upewnia się że model testowy jest dostępny"""
    import subprocess
    
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        if model_name not in result.stdout:
            # Próbuj pobrać model
            subprocess.run(['ollama', 'pull', model_name], timeout=300)
    except Exception:
        pytest.skip(f"Nie można zapewnić dostępności modelu {model_name}")

def create_test_pdf_with_multiple_pages(output_path: str, page_count: int = 3):
    """Tworzy testowy PDF z wieloma stronami"""
    # W prawdziwej implementacji użyłbyś biblioteki do generowania PDF
    content = b'%PDF-1.4\n'
    for i in range(page_count):
        content += f'% Page {i+1} content\n'.encode()
    content += b'%%EOF'
    
    with open(output_path, 'wb') as f:
        f.write(content)
