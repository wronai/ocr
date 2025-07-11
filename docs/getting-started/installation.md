# Instalacja systemu OCR

## Wymagania systemowe

- System operacyjny: Linux, macOS lub Windows 10/11
- Python 3.8 lub nowszy
- 8GB RAM (16GB zalecane)
- 10GB wolnego miejsca na dysku
- Karta graficzna z obsługą CUDA (opcjonalnie, ale zalecane)

## Instalacja krok po kroku

### 1. Instalacja Pythona

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

#### macOS (z użyciem Homebrew)
```bash
brew install python
```

#### Windows
Pobierz i zainstaluj Pythona ze strony: https://www.python.org/downloads/

### 2. Instalacja Ollama

#### Linux/macOS
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

#### Windows
Pobierz i zainstaluj Ollama ze strony: https://ollama.ai/download

### 3. Instalacja zależności systemowych

#### Ubuntu/Debian
```bash
sudo apt install -y libmagic1 poppler-utils tesseract-ocr
```

#### Fedora
```bash
sudo dnf install -y file poppler-utils tesseract
```

#### macOS
```bash
brew install poppler tesseract
```

### 4. Konfiguracja środowiska

1. Sklonuj repozytorium:
```bash
git clone https://github.com/wronai/ocr.git
cd ocr
```

2. Utwórz i aktywuj środowisko wirtualne:
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# lub
.\venv\Scripts\activate  # Windows
```

3. Zainstaluj zależności Pythona:
```bash
pip install -r requirements.txt
```

### 5. Pobranie modeli OCR

```bash
ollama pull llava:7b
# lub dla lepszej jakości (wymaga więcej zasobów)
# ollama pull llama3.2-vision
```

## Weryfikacja instalacji

Uruchom testową komendę, aby sprawdzić czy wszystko działa poprawnie:

```bash
python -c "import pdf_processor; print('Instalacja zakończona pomyślnie!')"
```

## Rozwiązywanie problemów

### Błąd braku bibliotek systemowych
Jeśli wystąpią błędy związane z brakującymi bibliotekami, zainstaluj odpowiednie pakiety:

#### Ubuntu/Debian
```bash
sudo apt install -y libxml2-dev libxslt-dev libjpeg-dev zlib1g-dev
```

#### Fedora
```bash
sudo dnf install -y libxml2-devel libxslt-devel libjpeg-devel zlib-devel
```

#### macOS
```bash
brew install libxml2 libxslt
```

### Problemy z Ollama
Jeśli Ollama nie działa poprawnie:
1. Upewnij się, że serwer Ollama działa:
   ```bash
   ollama serve
   ```
2. Sprawdź dostępne modele:
   ```bash
   ollama list
   ```
3. Jeśli potrzebujesz pomocy, zobacz dokumentację Ollama: https://github.com/ollama/ollama

## Następne kroki

- [Szybki start](../user-guide/quickstart.md) - jak szybko rozpocząć pracę z systemem
- [Konfiguracja](configuration.md) - jak dostosować ustawienia systemu do swoich potrzeb
