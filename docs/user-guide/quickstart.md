# Szybki start z systemem OCR

Ten przewodnik przeprowadzi Cię przez podstawowe funkcje systemu OCR, w tym nowe funkcje tłumaczenia i podglądu.

## Przygotowanie dokumentów

1. Utwórz katalog na dokumenty:
   ```bash
   mkdir -p documents
   ```

2. Skopiuj pliki PDF do przetworzenia:
   ```bash
   cp /ścieżka/do/dokumentów/*.pdf documents/
   ```

## Podstawowe przetwarzanie

### Przetwarzanie pojedynczego pliku

```bash
python proc.py --input documents/moj_dokument.pdf
```

### Przetwarzanie wsadowe

```bash
# Przetwórz wszystkie pliki PDF w katalogu
export OLLAMA_MODEL=llava:7b  # Wybierz model
python proc.py --input documents/ --output output/ --workers 4
```

## Nowe funkcje

### Tłumaczenie na język polski

Aby włączyć automatyczne tłumaczenie tekstu na język polski:

```bash
python proc.py --input dokument.pdf --translate
```

W interfejsie SVG możesz przełączać się między oryginalnym tekstem a tłumaczeniem używając przycisku "Pokaż tłumaczenie".

### Tryby wyświetlania

System oferuje dwa tryby wyświetlania stron:

1. **Tryb przewijania** (domyślny) - strony wyświetlane są jedna pod drugą
2. **Tryb siatki** - wiele stron wyświetlanych jest obok siebie

Przełączanie między trybami odbywa się za pomocą przycisków w prawym górnym rogu interfejsu.

### Interaktywne podświetlanie tekstu

- **Najechanie myszką** na fragment tekstu podświetla odpowiedni obszar na stronie
- **Kliknięcie** na podświetlony obszar pokazuje oryginalny tekst i tłumaczenie (jeśli dostępne)
- Użyj przycisku "Pokaż/schowaj podświetlenia" aby włączyć/wyłączyć tę funkcję

## Przykładowe przypadki użycia

### 1. Szybkie przetwarzanie z tłumaczeniem

```bash
python proc.py --input dokument_angielski.pdf --translate --model llava:7b
```

### 2. Wysoka jakość OCR

```bash
python proc.py --input ważny_dokument.pdf --model llama3.2-vision --dpi 300
```

### 3. Przetwarzanie wielu dokumentów

```bash
# Przetwórz wszystkie pliki PDF w katalogu i podkatalogach
find /ścieżka/do/dokumentów -name "*.pdf" -exec python proc.py --input {} \;
```

## Wyjście programu

Po przetworzeniu w katalogu wyjściowym znajdziesz:

- `nazwa_pliku_complete.svg` - interaktywny plik SVG z wynikami
- `nazwa_pliku_ocr.json` - dane OCR w formacie JSON
- `processing_report.json` - podsumowanie przetwarzania

## Rozwiązywanie problemów

### Niski poziom rozpoznania tekstu
- Zwiększ rozdzielczość DPI: `--dpi 300`
- Użyj lepszego modelu: `--model llama3.2-vision`
- Sprawdź jakość źródłowego dokumentu

### Problemy z tłumaczeniem
- Upewnij się, że masz połączenie z internetem
- Sprawdź czy wybrano język źródłowy, jeśli nie jest rozpoznawany automatycznie

## Następne kroki

- [Konfiguracja zaawansowana](../getting-started/configuration.md) - jak dostosować ustawienia systemu
- [Przykłady użycia](../examples/README.md) - więcej przykładów i przypadków użycia
- [Dokumentacja API](../api-reference/README.md) - szczegóły techniczne i integracja
