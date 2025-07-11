
"""
Pytest configuration and shared fixtures
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock
import os

@pytest.fixture(scope="session")
def temp_dir():
    """Session-scoped temporary directory"""
    tmp_dir = tempfile.mkdtemp()
    yield Path(tmp_dir)
    shutil.rmtree(tmp_dir)

@pytest.fixture
def mock_processor_dirs(temp_dir):
    """Mock directories for processor testing"""
    docs_dir = temp_dir / "documents"
    output_dir = temp_dir / "output"

    # Create directories if they don't exist
    docs_dir.mkdir(exist_ok=True)
    output_dir.mkdir(exist_ok=True)

    # Clear any existing files in the directories
    for file in docs_dir.glob("*"):
        if file.is_file():
            file.unlink()
    for file in output_dir.glob("*"):
        if file.is_file():
            file.unlink()

    return {
        "documents": str(docs_dir),
        "output": str(output_dir)
    }

@pytest.fixture
def sample_pdf_content():
    """Sample PDF content for testing"""
    return b"""%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj
3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]>>endobj
xref
0 4
0000000000 65535 f
0000000010 00000 n
0000000053 00000 n
0000000100 00000 n
trailer<</Size 4/Root 1 0 R>>
startxref
169
%%EOF"""

@pytest.fixture
def sample_pdf_file(temp_dir, sample_pdf_content):
    """Create a sample PDF file for testing"""
    pdf_file = temp_dir / "sample.pdf"
    pdf_file.write_bytes(sample_pdf_content)
    return str(pdf_file)

@pytest.fixture
def mock_ollama_response():
    """Mock successful Ollama response"""
    return {
        "text": "Sample extracted text from PDF",
        "confidence": 0.95,
        "language": "en",
        "blocks": [
            {
                "text": "Sample text block",
                "bbox": [10, 20, 100, 30],
                "confidence": 0.95
            }
        ]
    }

@pytest.fixture
def mock_failed_ollama_response():
    """Mock failed Ollama response"""
    return {
        "text": "",
        "confidence": 0.0,
        "language": "unknown",
        "blocks": [],
        "error": "OCR failed"
    }

# Skip markers for conditional testing
def pytest_configure(config):
    """Configure pytest markers"""
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "gpu: mark test as requiring GPU"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )

def pytest_collection_modifyitems(config, items):
    """Modify test collection based on markers"""
    if config.getoption("--no-slow"):
        skip_slow = pytest.mark.skip(reason="--no-slow option given")
        for item in items:
            if "slow" in item.keywords:
                item.add_marker(skip_slow)

def pytest_addoption(parser):
    """Add custom command line options"""
    parser.addoption(
        "--no-slow",
        action="store_true",
        default=False,
        help="skip slow tests"
    )
    parser.addoption(
        "--integration-only",
        action="store_true",
        default=False,
        help="run only integration tests"
    )
