# CHANGELOG.md

# 📅 Historia zmian

Wszystkie istotne zmiany w tym projekcie będą dokumentowane w tym pliku.

Format bazuje na [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
a projekt używa [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - Planowane funkcje

### Dodane
- [ ] Web UI interface (Streamlit)
- [ ] REST API endpoints
- [ ] GPU acceleration support
- [ ] Docker containers z Ollama
- [ ] Więcej modeli OCR (PaddleOCR, TrOCR)
- [ ] Real-time processing
- [ ] Advanced document understanding (tabele, formularze)

### Planowane poprawki
- [ ] Optymalizacja zużycia pamięci dla bardzo dużych plików
- [ ] Lepsze wsparcie dla różnych formatów PDF
- [ ] Automatyczne wykrywanie orientacji tekstu

---

## [2.0.0] - 2025-01-15 🚀

### Dodane
- **Kompletne przepisanie architektury** - nowa, bardziej modularna struktura
- **Przetwarzanie równoległe** - ThreadPoolExecutor dla szybszego OCR
- **Szczegółowe logowanie** - kompleksowy system logów z poziomami
- **Walidacja modeli Ollama** - sprawdzanie dostępności przed użyciem  
- **Optymalizacja pamięci** - automatyczna kompresja dużych obrazów
- **Robustna obsługa błędów** - graceful degradation i recovery
- **Interaktywny wybór modelu** - GUI w terminalu
- **Skrypty instalacyjne** - automatyczna instalacja wszystkich zależności
- **Szczegółowe raporty JSON** - metadane, statystyki, timeline
- **Konfiguracja YAML** - zewnętrzny plik konfiguracyjny
- **Cleanup automatyczny** - usuwanie plików tymczasowych
- **Timeout OCR** - zabezpieczenie przed zawieszaniem
- **Resize obrazów** - automatyczne dopasowanie rozmiaru dla wydajności
- **SVG z metadanymi** - wbudowane OCR data, searchable text
- **Weryfikacja instalacji** - kompleksowy test wszystkich komponentów

### Zmienione  
- **API klasy PDFOCRProcessor** - nowe metody i parametry
- **Format wyników** - rozszerzony o metadane i statystyki
- **Struktura SVG** - lepsze formatowanie i osadzanie obrazów
- **Wymagania systemowe** - Python 3.8+ (wcześniej 3.7+)
- **Format logów** - structured logging z timestamp
- **Strategia error handling** - bardziej szczegółowe błędy

### Poprawione
- **Interfejs Ollama** - właściwe API calls zamiast subprocess
- **Encoding problemów** - pełne wsparcie UTF-8 i polskich znaków
- **JSON parsing** - robustna obsługa błędnych odpowiedzi  
- **File path handling** - wsparcie dla spacji i znaków specjalnych
- **Memory leaks** - właściwe zamykanie zasobów
- **SVG validation** - sprawdzanie poprawności XML
- **Cross-platform compatibility** - testowane na Linux/macOS/Windows

### Usunięte
- Stary, jednowątkowy procesor OCR
- Podstawowa obsługa błędów bez szczegółów
- Hardkodowane ścieżki i konfiguracja

---

## [1.0.0] - 2025-01-10 📋

### Dodane
- **Podstawowa funkcjonalność OCR** z Ollama
- **Konwersja PDF → PNG** przez PyMuPDF  
- **Generowanie SVG** z wieloma stronami
- **Model llava:7b** jako domyślny
- **Batch processing** folderów PDF
- **Podstawowe raporty** w formacie JSON
- **CLI interface** - python pdf_processor.py

### Techniczne
- Python 3.7+ support
- PyMuPDF dla PDF processing
- Pillow dla image operations
- Subprocess calls do Ollama

---

## [0.9.0] - 2025-01-05 🔧

### Dodane
- **Proof of concept** - podstawowy OCR pipeline
- **Test integration** z Ollama
- **Przykładowe PDF** processing

### Ograniczenia znane w tej wersji
- Tylko pojedyncze pliki
- Brak error handling
- Hardkodowane ścieżki
- Brak testów

---

## Typy zmian

- **Dodane** - nowe funkcje
- **Zmienione** - zmiany w istniejących funkcjach  
- **Poprawione** - bugfixy
- **Usunięte** - usunięte funkcje
- **Zabezpieczenia** - w przypadku podatności
- **Przestarzałe** - funkcje które będą usunięte

---

# CONTRIBUTING.md

# 🤝 Przewodnik dla kontrybutorów

Dziękujemy za zainteresowanie rozwojem PDF OCR Processor! Ten przewodnik pomoże Ci w efektywnym wnoszeniu wkładu w projekt.

## 📋 Spis treści

1. [Jak zacząć](#jak-zacząć)
2. [Sposób pracy](#sposób-pracy)
3. [Standardy kodu](#standardy-kodu)
4. [Testowanie](#testowanie)
5. [Dokumentacja](#dokumentacja)
6. [Pull Requests](#pull-requests)
7. [Zgłaszanie błędów](#zgłaszanie-błędów)
8. [Roadmapa](#roadmapa)

---

## 🚀 Jak zacząć

### Przygotowanie środowiska deweloperskiego

```bash
# 1. Forkuj repozytorium na GitHub
# 2. Sklonuj swój fork
git clone https://github.com/YOUR_USERNAME/pdf-ocr-processor.git
cd pdf-ocr-processor

# 3. Dodaj upstream remote
git remote add upstream https://github.com/original-repo/pdf-ocr-processor.git

# 4. Uruchom setup dla developerów
make dev-setup
# lub ręcznie:
python -m venv venv
source venv/bin/activate  # Linux/macOS
pip install -r requirements-dev.txt
pre-commit install

# 5. Sprawdź czy wszystko działa
python verify_installation.py
make test
```

### Wybór zadania

1. **Sprawdź Issues** - znajdź zadanie oznaczone `good first issue` lub `help wanted`
2. **Roadmapa** - zobacz co jest planowane w kolejnych wersjach
3. **Dyskusje** - zadaj pytanie w GitHub Discussions
4. **Własny pomysł** - otwórz Issue z opisem propozycji

---

## 🔄 Sposób pracy

### Git workflow

Używamy **GitHub Flow** - prosty model oparty na feature branchach.

```bash
# 1. Synchronizuj z upstream
git checkout main
git pull upstream main

# 2. Stwórz feature branch
git checkout -b feature/nazwa-funkcji
# lub
git checkout -b fix/nazwa-buga
# lub  
git checkout -b docs/aktualizacja-dokumentacji

# 3. Wprowadź zmiany
# ... edytuj kod ...

# 4. Commit z opisową wiadomością
git add .
git commit -m "feat: dodaj obsługę GPU acceleration

- Integracja z CUDA dla modeli Ollama
- Automatyczne wykrywanie dostępnych GPU
- Fallback na CPU gdy GPU niedostępne
- Testy jednostkowe dla GPU operations

Closes #123"

# 5. Push do swojego fork
git push origin feature/nazwa-funkcji

# 6. Otwórz Pull Request na GitHub
```

### Konwencje commit messages

Używamy [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Typy:**
- `feat:` - nowa funkcja
- `fix:` - bugfix  
- `docs:` - dokumentacja
- `style:` - formatowanie (nie wpływa na logikę)
- `refactor:` - refaktoring bez zmian funkcji
- `test:` - dodawanie/modyfikacja testów
- `chore:` - maintenance, build, tools

**Przykłady:**
```bash
feat: dodaj wsparcie dla formatu DOCX
fix: napraw memory leak w PDF processing
docs: aktualizuj README z przykładami API
test: dodaj testy dla batch processing
refactor: wydziel OCR logic do oddzielnego modułu
chore: aktualizuj dependencies do najnowszych wersji
```

---

## 📝 Standardy kodu

### Python Code Style

Projekt używa **PEP 8** z następującymi narzędziami:

```bash
# Formatowanie
black pdf_processor/ tests/
isort pdf_processor/ tests/

# Linting
flake8 pdf_processor/ tests/
pylint pdf_processor/

# Type checking  
mypy pdf_processor/

# Wszystko jedną komendą
make lint
make format
```

### Konfiguracja narzędzi

**`.flake8`:**
```ini
[flake8]
max-line-length = 88
extend-ignore = E203, W503, E501
exclude = 
    .git,
    __pycache__,
    venv,
    build,
    dist
```

**`pyproject.toml`:**
```toml
[tool.black]
line-length = 88
target-version = ['py38']
include = '\.pyi?$'

[tool.isort]
profile = "black"
multi_line_output = 3

[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

### Struktura kodu

```python
#!/usr/bin/env python3
"""
Krótki opis modułu

Dłuższy opis funkcjonalności, przykłady użycia,
specjalne uwagi itp.
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

# Third party imports
import requests
from PIL import Image

# Local imports  
from pdf_processor.core import PDFProcessor
from pdf_processor.utils import logger


class ExampleClass:
    """
    Przykładowa klasa z dokumentacją
    
    Args:
        param1: Opis parametru
        param2: Inny parametr z domyślną wartością
        
    Attributes:
        attribute1: Publiczny atrybut
        _private_attr: Prywatny atrybut
    """
    
    def __init__(self, param1: str, param2: int = 10):
        self.attribute1 = param1
        self._private_attr = param2
        
    def public_method(self, data: List[str]) -> Dict[str, Any]:
        """
        Przykładowa publiczna metoda
        
        Args:
            data: Lista stringów do przetworzenia
            
        Returns:
            Słownik z wynikami przetwarzania
            
        Raises:
            ValueError: Gdy data jest pusta
            RuntimeError: Gdy wystąpi błąd przetwarzania
        """
        if not data:
            raise ValueError("Data cannot be empty")
            
        try:
            # Implementacja...
            result = {"processed": len(data)}
            return result
        except Exception as e:
            logger.error(f"Processing failed: {e}")
            raise RuntimeError(f"Failed to process data: {e}") from e
    
    def _private_method(self) -> None:
        """Prywatna metoda - krótki opis wystarczy"""
        pass


def utility_function(input_param: str) -> Optional[str]:
    """
    Funkcja narzędziowa
    
    Args:
        input_param: Parametr wejściowy
        
    Returns:
        Przetworzona wartość lub None jeśli błąd
    """
    # Implementacja...
    return input_param.upper() if input_param else None


if __name__ == "__main__":
    # Kod uruchamiany gdy plik jest skryptem
    pass
```

---

## 🧪 Testowanie

### Struktura testów

```
tests/
├── unit/                   # Testy jednostkowe
│   ├── test_pdf_processor.py
│   ├── test_ocr_engine.py
│   └── test_utils.py
├── integration/            # Testy integracyjne
│   ├── test_ollama_integration.py
│   └── test_end_to_end.py
├── performance/            # Testy wydajności
│   └── test_benchmarks.py
├── fixtures/               # Dane testowe
│   ├── sample.pdf
│   └── test_configs/
└── conftest.py            # Konfiguracja pytest
```

### Pisanie testów

```python
#!/usr/bin/env python3
"""
Przykład testów jednostkowych
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from pdf_processor import PDFOCRProcessor


class TestPDFOCRProcessor:
    """Testy dla klasy PDFOCRProcessor"""
    
    @pytest.fixture
    def processor(self):
        """Fixture z procesorem do testów"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            processor = PDFOCRProcessor(
                documents_folder=str(Path(tmp_dir) / "docs"),
                output_folder=str(Path(tmp_dir) / "output")
            )
            yield processor
    
    @pytest.fixture  
    def sample_pdf_path(self):
        """Fixture ze ścieżką do przykładowego PDF"""
        return "tests/fixtures/sample.pdf"
    
    def test_init_creates_directories(self, processor):
        """Test czy inicjalizacja tworzy katalogi"""
        assert processor.output_folder.exists()
        assert processor.documents_folder.exists()
    
    @patch('subprocess.run')
    def test_check_ollama_success(self, mock_run, processor):
        """Test sprawdzenia Ollama - sukces"""
        mock_run.return_value = Mock(returncode=0, stdout="llava:7b")
        
        models = processor.check_ollama_and_models()
        
        assert "llava:7b" in models
        mock_run.assert_called_once()
    
    @patch('subprocess.run')
    def test_check_ollama_failure(self, mock_run, processor):
        """Test sprawdzenia Ollama - błąd"""
        mock_run.return_value = Mock(returncode=1, stderr="not found")
        
        with pytest.raises(Exception, match="Ollama nie odpowiada"):
            processor.check_ollama_and_models()
    
    def test_extract_text_invalid_image(self, processor):
        """Test OCR z niepoprawnym obrazem"""
        result = processor.extract_text_with_ollama("/nonexistent/image.png")
        
        assert result["text"] == ""
        assert result["confidence"] == 0.0
        assert "error" in result
    
    @pytest.mark.slow
    def test_process_pdf_integration(self, processor, sample_pdf_path):
        """Test integracyjny przetwarzania PDF"""
        # Wymaga działającej instalacji Ollama
        pytest.importorskip("fitz")  # Skip if PyMuPDF not available
        
        result = processor.process_pdf(sample_pdf_path, "llava:7b")
        
        assert "error" not in result
        assert result["page_count"] > 0
        assert result["processing_time"] > 0
        assert 0 <= result["average_confidence"] <= 1.0


class TestUtilityFunctions:
    """Testy funkcji narzędziowych"""
    
    @pytest.mark.parametrize("input_val,expected", [
        ("hello", "HELLO"),
        ("", None),
        (None, None),
        ("MiXeD", "MIXED"),
    ])
    def test_utility_function(self, input_val, expected):
        """Test funkcji narzędziowej z parametryzacją"""
        from pdf_processor.utils import utility_function
        
        result = utility_function(input_val)
        assert result == expected


# Markery dla testów
pytestmark = [
    pytest.mark.unit,  # Wszystkie testy w tym pliku to unit tests
]

# Testy które wymagają specjalnych warunków
@pytest.mark.gpu  
def test_gpu_acceleration():
    """Test tylko gdy GPU dostępne"""
    pass

@pytest.mark.slow
def test_large_file_processing():
    """Długi test - uruchamiany osobno"""
    pass
```

### Uruchamianie testów

```bash
# Wszystkie testy
make test
# lub
pytest

# Tylko unit testy
pytest tests/unit/

# Z coverage
make test-cov
# lub
pytest --cov=pdf_processor --cov-report=html

# Konkretny test
pytest tests/unit/test_pdf_processor.py::TestPDFOCRProcessor::test_init

# Testy z określonym markerem
pytest -m "not slow"  # Bez testów oznaczonych jako slow
pytest -m gpu         # Tylko testy GPU

# Verbose output
pytest -v -s

# Zatrzymaj na pierwszym błędzie
pytest -x

# Uruchom ostatnio nieudane testy
pytest --lf
```

### Konfiguracja pytest

**`pytest.ini`:**
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --strict-markers
    --strict-config
    --verbose
markers =
    slow: oznacza testy które trwają długo
    gpu: testy wymagające GPU
    integration: testy integracyjne  
    unit: testy jednostkowe
```

---

## 📚 Dokumentacja

### Docstrings

Używamy **Google Style** docstrings:

```python
def process_document(file_path: str, model: str = "llava:7b", 
                    options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Przetwarza dokument PDF używając OCR.
    
    Ta funkcja konwertuje strony PDF na obrazy, wykonuje OCR
    używając określonego modelu Ollama i zwraca wyniki.
    
    Args:
        file_path: Ścieżka do pliku PDF do przetworzenia
        model: Nazwa modelu Ollama do użycia w OCR. Domyślnie "llava:7b"
        options: Opcjonalne parametry przetwarzania:
            - dpi (int): Rozdzielczość konwersji, domyślnie 200
            - parallel (bool): Czy używać przetwarzania równoległego
            - timeout (int): Timeout w sekundach, domyślnie 300
    
    Returns:
        Słownik z wynikami przetwarzania:
            {
                "page_count": int,
                "processing_time": float,
                "ocr_results": List[Dict],
                "average_confidence": float,
                "svg_path": Optional[str]
            }
    
    Raises:
        FileNotFoundError: Gdy plik PDF nie istnieje
        ValueError: Gdy model nie jest dostępny
        RuntimeError: Gdy wystąpi błąd podczas przetwarzania
        
    Example:
        >>> processor = PDFOCRProcessor()
        >>> result = processor.process_pdf("document.pdf", "llava:7b")
        >>> print(f"Przetworzono {result['page_count']} stron")
        Przetworzono 5 stron
        
    Note:
        Funkcja automatycznie tworzy katalog wyjściowy jeśli nie istnieje.
        Dla dokumentów wielostronicowych generowany jest plik SVG.
        
    See Also:
        process_all_pdfs: Przetwarzanie wielu plików naraz
        extract_text_with_ollama: Niskopoziomowe API dla OCR
    """
```

### README i dokumentacja

- **README.md** - główna dokumentacja, zawsze aktualna
- **EXAMPLES.md** - praktyczne przykłady użycia
- **QUICK_START.md** - przewodnik dla nowych użytkowników
- **docs/** - dodatkowa dokumentacja techniczna

### Aktualizacja dokumentacji

```bash
# Sprawdź czy docstrings są aktualne
make docs-check

# Generuj dokumentację HTML
make docs

# Serwuj dokumentację lokalnie
make docs-serve
```

---

## 🔄 Pull Requests

### Checklist przed PR

- [ ] **Kod zgodny ze standardami** - `make lint` przechodzi
- [ ] **Testy napisane** - coverage dla nowych funkcji
- [ ] **Testy przechodzą** - `make test` sukces  
- [ ] **Dokumentacja zaktualizowana** - docstrings, README
- [ ] **Commit messages zgodne** z Conventional Commits
- [ ] **Changelog zaktualizowany** jeśli znacząca zmiana
- [ ] **No merge conflicts** z main branch

### Template PR

Gdy otwierasz PR, użyj tego template:

```markdown
## 📋 Opis zmian

Krótki opis co zostało zmienione i dlaczego.

## 🔗 Powiązane Issues

Closes #123
Related to #456

## 🧪 Typ zmian

- [ ] Bug fix (non-breaking change)
- [ ] New feature (non-breaking change)  
- [ ] Breaking change (existing functionality affected)
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring

## ✅ Testing

- [ ] Unit tests added/updated
- [ ] Integration tests passed
- [ ] Manual testing completed
- [ ] Performance impact assessed

## 📝 Screenshots/Logs

<!-- Jeśli dotyczy, dodaj screenshots lub logi -->

## 📚 Documentation

- [ ] Code comments updated
- [ ] README updated if needed
- [ ] Examples added/updated
- [ ] Changelog updated

## ⚠️ Breaking Changes

<!-- Opisz breaking changes jeśli występują -->

## 🔍 Review Notes

<!-- Dodatkowe informacje dla reviewers -->
```

### Review proces

1. **Automated checks** - CI/CD musi przejść
2. **Code review** - przynajmniej 1 approval od maintainera
3. **Testing** - reviewer testuje funkcjonalność
4. **Documentation** - sprawdzenie czy docs są aktualne
5. **Merge** - squash and merge lub rebase (w zależności od sytuacji)

---

## 🐛 Zgłaszanie błędów

### Bug Report Template

```markdown
**🐛 Opis błędu**
Jasny i zwięzły opis problemu.

**🔄 Kroki do odtworzenia**
1. Przejdź do '...'
2. Kliknij na '...'
3. Przewiń do '...'
4. Zobacz błąd

**✅ Oczekiwane zachowanie**
Opis tego co powinno się stać.

**❌ Rzeczywiste zachowanie**  
Opis tego co się dzieje zamiast tego.

**🖼️ Screenshots/Logi**
Jeśli dotyczy, dodaj screenshots lub logi błędów.

**🖥️ Środowisko**
- OS: [np. Ubuntu 20.04, macOS 12.0, Windows 10]
- Python: [np. 3.9.7]
- PDF OCR Processor: [np. 2.0.0]
- Ollama: [np. 0.1.17]

**📄 Przykładowy plik**
Jeśli możliwe, załącz PDF który powoduje problem (upewnij się że nie zawiera danych wrażliwych).

**📝 Dodatkowy kontekst**
Inne informacje które mogą pomóc w rozwiązaniu problemu.
```

### Feature Request Template  

```markdown
**🚀 Opis funkcji**
Jasny opis żądanej funkcjonalności.

**❓ Problem do rozwiązania**
Jaki problem ta funkcja rozwiązuje? Czy istnieją obejścia?

**💡 Proponowane rozwiązanie**
Opis jak widzisz implementację tej funkcji.

**🔄 Alternatywy**
Inne sposoby rozwiązania tego problemu.

**📈 Use case**
Konkretny przykład użycia tej funkcji.

**🎯 Priorytet**
- [ ] Nice to have
- [ ] Important  
- [ ] Critical

**📝 Dodatkowy kontekst**
Screenshots, mockupy, linki do podobnych rozwiązań itp.
```

---

## 🗺️ Roadmapa

### Najbliższe planowane funkcje (v2.1)

**Wysokie priorytety:**
- [ ] **Web UI** - Streamlit interface dla łatwego użycia
- [ ] **REST API** - Endpoints dla integracji z innymi systemami  
- [ ] **Docker containers** - Łatwy deployment
- [ ] **GPU acceleration** - Wsparcie dla CUDA/Metal

**Średnie priorytety:**
- [ ] **Więcej modeli OCR** - PaddleOCR, TrOCR, EasyOCR
- [ ] **Document understanding** - Wykrywanie tabel, formularzy
- [ ] **Batch API** - Async processing wielu dokumentów
- [ ] **Cloud deployment** - AWS/GCP/Azure templates

**Niskie priorytety:**
- [ ] **Real-time processing** - Live PDF processing
- [ ] **Advanced analytics** - NLP analysis of extracted text
- [ ] **Multi-language optimization** - Lepsze wsparcie dla różnych języków
- [ ] **Enterprise features** - LDAP auth, audit logs

### Jak przyczynić się do roadmapy

1. **Implementuj funkcję** - wybierz z listy i otwórz PR
2. **Zaproponuj nową** - otwórz Feature Request Issue
3. **Pomóż w priorytetyzacji** - głosuj na Issues (👍/👎)
4. **Beta testing** - testuj nowe funkcje w development branch

---

## 🏆 Typy kontrybutorów

### 🐛 Bug Hunters
- Znajdowanie i zgłaszanie błędów
- Testowanie edge cases  
- Weryfikacja bugfixes

### 💻 Developers  
- Implementacja nowych funkcji
- Bugfixy
- Performance optimizations
- Code refactoring

### 📝 Documentation Writers
- Aktualizacja README i dokumentacji
- Pisanie tutoriali i przykładów
- Tłumaczenia na inne języki

### 🧪 Quality Assurance
- Pisanie testów
- Code review
- Performance testing
- Security audits  

### 🎨 UX/UI Designers
- Projektowanie web interface
- User experience improvements
- Mockupy i wireframes

### 📊 DevOps/Infrastructure  
- CI/CD pipelines
- Docker containers
- Cloud deployment
- Monitoring & alerting

---

## 📞 Komunikacja

### Kanały komunikacji

- **GitHub Issues** - bugs, feature requests, Q&A
- **GitHub Discussions** - ogólne dyskusje, pomysły
- **Discord** - real-time chat społeczności (link w README)
- **Email** - kontakt z maintainerami: team@pdf-ocr-processor.com

### Code of Conduct

Projekt przestrzega [Contributor Covenant](https://www.contributor-covenant.org/). 

**Krótko:**
- Bądź życzliwy i szanuj innych
- Konstruktywna krytyka, nie personal attacks
- Pomóż innym się uczyć
- Zgłaszaj nieodpowiednie zachowania

---

## 🎉 Uznania

Wszyscy kontrybutorzy są wymienieni w:
- **README.md** - sekcja Contributors
- **CONTRIBUTORS.md** - pełna lista z opisem wkładu
- **Release notes** - podziękowania w changelog

---

**Dziękujemy za pomoc w rozwijaniu PDF OCR Processor! 🚀**

*Ostatnia aktualizacja: 15 stycznia 2025*