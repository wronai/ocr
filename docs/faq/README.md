# Często zadawane pytania (FAQ)

## 📦 Instalacja i konfiguracja

### Jak zainstalować wymagane zależności systemowe?

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv libmagic1 poppler-utils tesseract-ocr
```

#### Fedora
```bash
sudo dnf install -y python3 python3-pip poppler-utils tesseract
```

#### macOS
```bash
brew install python poppler tesseract
```

### Jak zainstalować Ollama?

#### Linux/macOS
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

#### Windows
Pobierz instalator ze strony: https://ollama.ai/download

## 🛠 Użytkowanie

### Jak przetworzyć wiele plików PDF naraz?

```bash
# Przetwórz wszystkie pliki PDF w katalogu
python proc.py --input /ścieżka/do/pliki/*.pdf --output wyniki/

# Rekurencyjnie przetwórz wszystkie pliki PDF w podkatalogach
find /ścieżka/do/katalogu -name "*.pdf" -exec python proc.py --input {} \;
```

### Jak poprawić jakość rozpoznawania tekstu?

1. Zwiększ rozdzielczość DPI:
   ```bash
   python proc.py --input dokument.pdf --dpi 300
   ```

2. Użyj lepszego modelu OCR:
   ```bash
   python proc.py --input dokument.pdf --model llama3.2-vision
   ```

3. Przetwarzaj oryginalne pliki PDF zamiast zeskanowanych dokumentów

### Jak włączyć tłumaczenie na język polski?

```bash
python proc.py --input dokument.pdf --translate
```

W interfejsie SVG użyj przycisku "Pokaż tłumaczenie" aby przełączać się między oryginałem a tłumaczeniem.

## 🖥️ Wyświetlanie

### Jak zmienić tryb wyświetlania stron?

W interfejsie SVG użyj przycisków w prawym górnym rogu:
- "Widok przewijania" - strony jedna pod drugą
- "Widok siatki" - wiele stron obok siebie

### Jak wyłączyć podświetlanie rozpoznanego tekstu?

Użyj przycisku "Pokaż/schowaj podświetlenia" w interfejsie SVG lub uruchom przetwarzanie z opcją:

```bash
python proc.py --input dokument.pdf --no-highlights
```

## ⚡ Wydajność

### Jak przyspieszyć przetwarzanie?

1. Zwiększ liczbę wątków roboczych:
   ```bash
   python proc.py --input dokument.pdf --workers 8
   ```

2. Zmniejsz rozdzielczość DPI:
   ```bash
   python proc.py --input dokument.pdf --dpi 150
   ```

3. Użyj szybszego modelu:
   ```bash
   python proc.py --input dokument.pdf --model llava:7b
   ```

### Jakie są wymagania sprzętowe?

- **Minimalne:**
  - 4GB RAM
  - Procesor dwurdzeniowy
  - 5GB wolnego miejsca na dysku

- **Zalecane:**
  - 16GB RAM
  - Procesor czterordzeniowy
  - Karta graficzna z obsługą CUDA
  - 20GB wolnego miejsca na dysku

## 🐛 Rozwiązywanie problemów

### Błąd: "Nie można załadować biblioteki współdzielonej"

Zainstaluj brakujące zależności systemowe:

#### Ubuntu/Debian
```bash
sudo apt install -y libsm6 libxext6 libxrender-dev
```

#### Fedora
```bash
sudo dnf install -y libSM libXext libXrender
```

### Błąd: "Brak miejsca na dysku"

1. Wyczyść katalog tymczasowy:
   ```bash
   rm -rf temp/*
   ```

2. Określ inny katalog tymczasowy:
   ```bash
   python proc.py --input dokument.pdf --temp-dir /ścieżka/do/dużego/dysku/temp
   ```

### Tłumaczenie nie działa

1. Sprawdź połączenie z internetem
2. Upewnij się, że podałeś poprawny klucz API (jeśli wymagany)
3. Sprawdź limity użycia usługi tłumaczącej

## 📚 Dodatkowe zasoby

- [Dokumentacja Ollama](https://github.com/ollama/ollama)
- [Dokumentacja Pythona](https://docs.python.org/3/)
- [Dokumentacja Pillow (PIL)](https://pillow.readthedocs.io/)

## ❓ Nie znalazłeś odpowiedzi?

Jeśli masz pytanie, na które nie ma odpowiedzi w tej dokumentacji, [zgłoś problem](https://github.com/wronai/ocr/issues) w naszym repozytorium.
