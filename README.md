# OCR Processing System

> Narzędzie do przetwarzania dokumentów PDF z zaawansowanym OCR, tłumaczeniem i wizualizacją

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Documentation](https://img.shields.io/badge/Docs-Read%20the%20Docs-blueviolet)](docs/README.md)

## 🚀 Funkcje

- **Zaawansowane OCR** z wykorzystaniem modeli AI (Ollama)
- **Tłumaczenie** tekstu na język polski
- **Dwie wersje wyświetlania**:
  - Tryb przewijania (strona po stronie)
  - Tryb siatki (podgląd wielu stron)
- **Interaktywne podświetlanie** rozpoznanego tekstu
- **Eksport do SVG** z zachowaniem warstw tekstu

## 📦 Instalacja

1. **Wymagania wstępne**
   - Python 3.8+
   - Ollama (https://ollama.ai)
   - Systemowe zależności (zobacz [Instalacja](docs/getting-started/installation.md))

2. **Instalacja**
   ```bash
   # Sklonuj repozytorium
   git clone https://github.com/wronai/ocr.git
   cd ocr
   
   # Utwórz i aktywuj środowisko wirtualne
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # lub
   .\venv\Scripts\activate  # Windows
   
   # Zainstaluj zależności
   pip install -r requirements.txt
   ```

## 🏁 Szybki start

1. **Przygotuj dokumenty**
   ```bash
   mkdir -p documents
   cp /ścieżka/do/twoich/plików/*.pdf documents/
   ```

2. **Uruchom przetwarzanie**
   ```bash
   python proc.py --model llava:7b --workers 4
   ```

3. **Zobacz wyniki**
   - Otwórz plik `output/*_complete.svg` w przeglądarce
   - Sprawdź szczegóły w `output/processing_report.json`

## 📚 Dokumentacja

Pełna dokumentacja dostępna w katalogu [docs/](docs/):

- [📖 Przewodnik użytkownika](docs/user-guide/README.md)
- [⚙️ Instalacja i konfiguracja](docs/getting-started/installation.md)
- [🔧 Referencja API](docs/api-reference/README.md)
- [❓ Często zadawane pytania](docs/faq/README.md)
- [👨‍💻 Rozwój i współtworzenie](docs/development/contributing.md)

## 📝 Licencja

Ten projekt jest dostępny na licencji MIT. Zobacz plik [LICENSE](LICENSE) aby uzyskać więcej informacji.

## 🤝 Współtworzenie

Wkład jest mile widziany! Zobacz [przewodnik współtworzenia](docs/development/contributing.md) aby dowiedzieć się więcej o tym, jak możesz pomóc w rozwoju projektu.
