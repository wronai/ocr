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
