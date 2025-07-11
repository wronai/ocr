# 💡 Przykłady użycia PDF OCR Processor

Ten plik zawiera praktyczne przykłady użycia PDF OCR Processor w różnych scenariuszach.

## 📋 Spis treści

1. [Podstawowe użycie](#podstawowe-użycie)
2. [Integracja z Python](#integracja-z-python)
3. [Batch processing](#batch-processing)
4. [Analiza wyników](#analiza-wyników)
5. [Automatyzacja](#automatyzacja)
6. [Integracje zewnętrzne](#integracje-zewnętrzne)
7. [Optymalizacja wydajności](#optymalizacja-wydajności)

---

## 🚀 Podstawowe użycie

### Przykład 1: Przetworzenie pojedynczego dokumentu

```bash
# Umieść PDF w folderze documents
cp ~/Pobrane/faktura.pdf documents/

# Uruchom przetwarzanie
python pdf_processor.py

# Sprawdź wyniki
ls output/faktura/
# output/faktura/page_001.png
# output/faktura/page_002.png
# output/faktura_complete.svg
```

### Przykład 2: Wybór konkretnego modelu OCR

```bash
# Lista dostępnych modeli
ollama list

# Użyj najdokładniejszego modelu
python pdf_processor.py --model llama3.2-vision --dpi 300

# Szybkie przetwarzanie
python pdf_processor.py --model llava:7b --dpi 150
```

---

## 🐍 Integracja z Python

### Przykład 1: Podstawowe API

```python
#!/usr/bin/env python3
"""
Przykład podstawowego użycia PDF OCR Processor
"""

from pdf_processor import PDFOCRProcessor
import json

def process_single_pdf():
    """Przetwórz pojedynczy PDF"""
    # Inicjalizuj processor
    processor = PDFOCRProcessor(
        documents_folder="my_documents",
        output_folder="my_output"
    )
    
    # Przetwórz dokument
    result = processor.process_pdf(
        pdf_path="my_documents/contract.pdf",
        model="llava:7b",
        parallel_ocr=True
    )
    
    # Sprawdź wyniki
    if "error" not in result:
        print(f"✅ Przetworzono {result['page_count']} stron")
        print(f"📄 Całkowity tekst: {result['total_text_length']} znaków")
        print(f"🎯 Średnia pewność: {result['average_confidence']:.2%}")
        
        # Wyciągnij cały tekst
        full_text = "\n\n".join(
            ocr_result.get("text", "") 
            for ocr_result in result["ocr_results"]
        )
        
        # Zapisz tekst do pliku
        with open("extracted_text.txt", "w", encoding="utf-8") as f:
            f.write(full_text)
            
        print(f"💾 Tekst zapisany do: extracted_text.txt")
    else:
        print(f"❌ Błąd: {result['error']}")

if __name__ == "__main__":
    process_single_pdf()
```

### Przykład 2: Zaawansowana analiza wyników

```python
#!/usr/bin/env python3
"""
Zaawansowana analiza wyników OCR
"""

from pdf_processor import PDFOCRProcessor
import re
from collections import Counter
import matplotlib.pyplot as plt

class OCRAnalyzer:
    def __init__(self, processor_results):
        self.results = processor_results
        self.all_text = self._extract_all_text()
    
    def _extract_all_text(self):
        """Wyciągnij cały tekst z wyników"""
        texts = []
        for result in self.results:
            if "ocr_results" in result:
                for ocr in result["ocr_results"]:
                    texts.append(ocr.get("text", ""))
        return " ".join(texts)
    
    def find_emails(self):
        """Znajdź wszystkie adresy email"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return re.findall(email_pattern, self.all_text)
    
    def find_phone_numbers(self):
        """Znajdź numery telefonów (polskie)"""
        phone_patterns = [
            r'\b\d{3}[-\s]?\d{3}[-\s]?\d{3}\b',  # 123-456-789
            r'\b\+48[-\s]?\d{3}[-\s]?\d{3}[-\s]?\d{3}\b',  # +48 123 456 789
            r'\b\d{2}[-\s]?\d{3}[-\s]?\d{2}[-\s]?\d{2}\b'  # 12 345 67 89
        ]
        
        phones = []
        for pattern in phone_patterns:
            phones.extend(re.findall(pattern, self.all_text))
        return phones
    
    def find_dates(self):
        """Znajdź daty w różnych formatach"""
        date_patterns = [
            r'\b\d{1,2}[./]\d{1,2}[./]\d{4}\b',  # DD.MM.YYYY
            r'\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b',  # YYYY-MM-DD
            r'\b\d{1,2}\s+(stycznia|lutego|marca|kwietnia|maja|czerwca|lipca|sierpnia|września|października|listopada|grudnia)\s+\d{4}\b'
        ]
        
        dates = []
        for pattern in date_patterns:
            dates.extend(re.findall(pattern, self.all_text, re.IGNORECASE))
        return dates
    
    def analyze_confidence(self):
        """Analizuj poziom pewności OCR"""
        confidences = []
        page_confidences = []
        
        for result in self.results:
            if "ocr_results" in result:
                for i, ocr in enumerate(result["ocr_results"]):
                    conf = ocr.get("confidence", 0.0)
                    confidences.append(conf)
                    page_confidences.append((result["pdf_path"], i+1, conf))
        
        return {
            "average": sum(confidences) / len(confidences) if confidences else 0,
            "min": min(confidences) if confidences else 0,
            "max": max(confidences) if confidences else 0,
            "per_page": page_confidences
        }
    
    def word_frequency(self, top_n=20):
        """Analiza częstotliwości słów"""
        # Oczyść tekst
        words = re.findall(r'\b[a-ząćęłńóśźż]{3,}\b', self.all_text.lower())
        
        # Usuń stop words (podstawowe)
        stop_words = {'dla', 'lub', 'oraz', 'jest', 'jako', 'które', 'przez', 
                     'tego', 'będzie', 'może', 'tylko', 'bardzo', 'gdzie'}
        words = [w for w in words if w not in stop_words]
        
        return Counter(words).most_common(top_n)
    
    def generate_report(self):
        """Wygeneruj kompletny raport analizy"""
        emails = self.find_emails()
        phones = self.find_phone_numbers()
        dates = self.find_dates()
        confidence_stats = self.analyze_confidence()
        top_words = self.word_frequency()
        
        report = {
            "document_stats": {
                "total_documents": len(self.results),
                "total_text_length": len(self.all_text),
                "word_count": len(self.all_text.split())
            },
            "extracted_data": {
                "emails": emails,
                "phone_numbers": phones,
                "dates": dates
            },
            "ocr_quality": confidence_stats,
            "content_analysis": {
                "top_words": top_words
            }
        }
        
        return report

# Przykład użycia
def analyze_processing_results():
    """Analizuj wyniki przetwarzania"""
    processor = PDFOCRProcessor()
    
    # Przetwórz wszystkie PDFy
    results = processor.process_all_pdfs("llava:7b")
    
    # Analizuj wyniki
    analyzer = OCRAnalyzer(results)
    report = analyzer.generate_report()
    
    # Wyświetl raport
    print("📊 RAPORT ANALIZY OCR")
    print("=" * 40)
    
    print(f"📄 Dokumenty: {report['document_stats']['total_documents']}")
    print(f"📝 Słowa: {report['document_stats']['word_count']}")
    print(f"🎯 Średnia pewność: {report['ocr_quality']['average']:.2%}")
    
    print(f"\n📧 Znalezione emaile ({len(report['extracted_data']['emails'])}):")
    for email in report['extracted_data']['emails'][:5]:
        print(f"  • {email}")
    
    print(f"\n📞 Numery telefonów ({len(report['extracted_data']['phone_numbers'])}):")
    for phone in report['extracted_data']['phone_numbers'][:5]:
        print(f"  • {phone}")
    
    print(f"\n📅 Znalezione daty ({len(report['extracted_data']['dates'])}):")
    for date in report['extracted_data']['dates'][:5]:
        print(f"  • {date}")
    
    print(f"\n🔤 Najczęstsze słowa:")
    for word, count in report['content_analysis']['top_words'][:10]:
        print(f"  • {word}: {count}")
    
    # Zapisz pełny raport
    import json
    with open("analysis_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Pełny raport zapisany: analysis_report.json")

if __name__ == "__main__":
    analyze_processing_results()
```

---

## 📦 Batch processing

### Przykład 1: Przetwarzanie folderów z kategoryzacją

```python
#!/usr/bin/env python3
"""
Batch processing z kategoryzacją dokumentów
"""

import os
from pathlib import Path
from pdf_processor import PDFOCRProcessor
import shutil

class BatchProcessor:
    def __init__(self, base_folder="documents"):
        self.base_folder = Path(base_folder)
        self.categories = {
            "faktury": ["faktura", "invoice", "rachunek"],
            "umowy": ["umowa", "contract", "agreement"],
            "raporty": ["raport", "report", "analiza"],
            "inne": []  # fallback
        }
    
    def categorize_pdf(self, pdf_path):
        """Kategoryzuj PDF na podstawie nazwy"""
        filename = pdf_path.name.lower()
        
        for category, keywords in self.categories.items():
            if any(keyword in filename for keyword in keywords):
                return category
        
        return "inne"
    
    def process_by_category(self):
        """Przetwarzaj PDFy według kategorii"""
        # Znajdź wszystkie PDFy
        pdf_files = list(self.base_folder.glob("**/*.pdf"))
        
        # Grupuj według kategorii
        categorized = {}
        for pdf_file in pdf_files:
            category = self.categorize_pdf(pdf_file)
            if category not in categorized:
                categorized[category] = []
            categorized[category].append(pdf_file)
        
        results = {}
        
        # Przetwarzaj każdą kategorię
        for category, files in categorized.items():
            print(f"\n📂 Przetwarzanie kategorii: {category} ({len(files)} plików)")
            
            # Stwórz folder dla kategorii
            category_output = Path("output") / category
            category_output.mkdir(parents=True, exist_ok=True)
            
            processor = PDFOCRProcessor(
                documents_folder=str(self.base_folder),
                output_folder=str(category_output)
            )
            
            category_results = []
            for pdf_file in files:
                print(f"  🔄 {pdf_file.name}")
                result = processor.process_pdf(str(pdf_file))
                category_results.append(result)
            
            results[category] = category_results
        
        return results

# Przykład użycia
if __name__ == "__main__":
    processor = BatchProcessor()
    results = processor.process_by_category()
    
    # Podsumowanie
    for category, category_results in results.items():
        successful = len([r for r in category_results if "error" not in r])
        total = len(category_results)
        print(f"📊 {category}: {successful}/{total} dokumentów przetworzonych")
```

### Przykład 2: Przetwarzanie z priorytetami

```bash
#!/bin/bash
# priority_processing.sh - Przetwarzanie z priorytetami

# Funkcja do przetwarzania z priorytetem
process_priority() {
    local priority=$1
    local folder=$2
    local model=$3
    local workers=$4
    
    echo "🔄 Priorytet $priority: $folder"
    python pdf_processor.py \
        --documents "$folder" \
        --output "output/priority_$priority" \
        --model "$model" \
        --workers "$workers"
}

# Wysokie priorytety - najlepszy model, mało workerów (jakość)
echo "🚨 Wysokie priorytety"
process_priority "high" "documents/urgent" "llama3.2-vision" 2

# Średnie priorytety - balans jakość/szybkość  
echo "⚡ Średnie priorytety"
process_priority "medium" "documents/normal" "llava:7b" 4

# Niskie priorytety - szybko, dużo workerów
echo "📦 Niskie priorytety"
process_priority "low" "documents/archive" "llava:7b" 8

echo "✅ Wszystkie priorytety zakończone"
```

---

## 📊 Analiza wyników

### Przykład 1: Dashboard statystyk

```python
#!/usr/bin/env python3
"""
Dashboard do analizy wyników OCR
"""

import json
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import pandas as pd

class OCRDashboard:
    def __init__(self, report_path="output/processing_report.json"):
        with open(report_path, 'r', encoding='utf-8') as f:
            self.report = json.load(f)
    
    def plot_confidence_distribution(self):
        """Wykres rozkładu poziomów pewności"""
        confidences = []
        
        for result in self.report.get("file_results", []):
            if "ocr_results" in result:
                for ocr in result["ocr_results"]:
                    confidences.append(ocr.get("confidence", 0.0))
        
        plt.figure(figsize=(10, 6))
        plt.hist(confidences, bins=20, alpha=0.7, color='skyblue', edgecolor='black')
        plt.title('Rozkład poziomów pewności OCR')
        plt.xlabel('Poziom pewności')
        plt.ylabel('Liczba stron')
        plt.grid(True, alpha=0.3)
        plt.axvline(x=sum(confidences)/len(confidences), color='red', 
                   linestyle='--', label=f'Średnia: {sum(confidences)/len(confidences):.2f}')
        plt.legend()
        plt.savefig('confidence_distribution.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_processing_times(self):
        """Wykres czasów przetwarzania"""
        files = []
        times = []
        pages = []
        
        for result in self.report.get("file_results", []):
            if "processing_time" in result and "page_count" in result:
                files.append(Path(result["pdf_path"]).name)
                times.append(result["processing_time"])
                pages.append(result["page_count"])
        
        plt.figure(figsize=(12, 8))
        
        # Wykres czasów przetwarzania
        plt.subplot(2, 1, 1)
        plt.bar(range(len(files)), times, color='lightcoral')
        plt.title('Czasy przetwarzania dokumentów')
        plt.ylabel('Czas (sekundy)')
        plt.xticks(range(len(files)), [f[:15] + '...' if len(f) > 15 else f 
                                      for f in files], rotation=45)
        
        # Wykres czasu na stronę
        plt.subplot(2, 1, 2)
        time_per_page = [t/p if p > 0 else 0 for t, p in zip(times, pages)]
        plt.bar(range(len(files)), time_per_page, color='lightgreen')
        plt.title('Czas przetwarzania na stronę')
        plt.ylabel('Czas/strona (sekundy)')
        plt.xticks(range(len(files)), [f[:15] + '...' if len(f) > 15 else f 
                                      for f in files], rotation=45)
        
        plt.tight_layout()
        plt.savefig('processing_times.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def create_summary_table(self):
        """Stwórz tabelę podsumowującą"""
        data = []
        
        for result in self.report.get("file_results", []):
            if "error" not in result:
                data.append({
                    'Plik': Path(result["pdf_path"]).name,
                    'Strony': result.get("page_count", 0),
                    'Czas (s)': round(result.get("processing_time", 0), 1),
                    'Czas/strona (s)': round(result.get("processing_time", 0) / 
                                           max(result.get("page_count", 1), 1), 2),
                    'Średnia pewność': f"{result.get('average_confidence', 0):.1%}",
                    'Długość tekstu': result.get("total_text_length", 0),
                    'SVG': "✅" if result.get("svg_path") else "❌"
                })
        
        df = pd.DataFrame(data)
        
        print("📊 PODSUMOWANIE PRZETWARZANIA")
        print("=" * 80)
        print(df.to_string(index=False))
        
        # Zapisz do CSV
        df.to_csv('processing_summary.csv', index=False, encoding='utf-8')
        print(f"\n💾 Tabela zapisana: processing_summary.csv")
        
        return df

# Przykład użycia
if __name__ == "__main__":
    dashboard = OCRDashboard()
    
    # Wygeneruj wykresy
    dashboard.plot_confidence_distribution()
    dashboard.plot_processing_times()
    
    # Stwórz tabelę
    summary_df = dashboard.create_summary_table()
```

---

## 🤖 Automatyzacja

### Przykład 1: Watch folder - automatyczne przetwarzanie

```python
#!/usr/bin/env python3
"""
Automatyczne przetwarzanie nowych plików PDF
"""

import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pdf_processor import PDFOCRProcessor
from pathlib import Path
import logging

class PDFWatcher(FileSystemEventHandler):
    def __init__(self, watch_folder="documents/inbox", 
                 processed_folder="documents/processed",
                 output_folder="output"):
        self.watch_folder = Path(watch_folder)
        self.processed_folder = Path(processed_folder)
        self.output_folder = Path(output_folder)
        
        # Stwórz foldery jeśli nie istnieją
        self.watch_folder.mkdir(parents=True, exist_ok=True)
        self.processed_folder.mkdir(parents=True, exist_ok=True)
        self.output_folder.mkdir(parents=True, exist_ok=True)
        
        # Inicjalizuj processor
        self.processor = PDFOCRProcessor(
            documents_folder=str(self.watch_folder),
            output_folder=str(self.output_folder)
        )
        
        # Konfiguruj logowanie
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('pdf_watcher.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def on_created(self, event):
        """Obsłuż utworzenie nowego pliku"""
        if event.is_dir:
            return
        
        file_path = Path(event.src_path)
        
        # Sprawdź czy to PDF
        if file_path.suffix.lower() == '.pdf':
            self.logger.info(f"Nowy PDF wykryty: {file_path.name}")
            
            # Poczekaj chwilę (plik może być jeszcze kopiowany)
            time.sleep(2)
            
            # Przetwórz PDF
            self.process_pdf(file_path)
    
    def process_pdf(self, pdf_path):
        """Przetwórz pojedynczy PDF"""
        try:
            self.logger.info(f"Rozpoczynam przetwarzanie: {pdf_path.name}")
            
            # Przetwórz
            result = self.processor.process_pdf(str(pdf_path), "llava:7b")
            
            if "error" not in result:
                self.logger.info(f"✅ Sukces: {pdf_path.name} "
                               f"({result['page_count']} stron, "
                               f"{result['processing_time']:.1f}s)")
                
                # Przenieś do folderu processed
                processed_path = self.processed_folder / pdf_path.name
                pdf_path.rename(processed_path)
                self.logger.info(f"📁 Przeniesiono do: {processed_path}")
                
            else:
                self.logger.error(f"❌ Błąd przetwarzania {pdf_path.name}: "
                                f"{result['error']}")
                
        except Exception as e:
            self.logger.error(f"❌ Wyjątek podczas przetwarzania {pdf_path.name}: {e}")

def start_pdf_watcher():
    """Uruchom obserwatora folderów"""
    watcher = PDFWatcher()
    observer = Observer()
    observer.schedule(watcher, str(watcher.watch_folder), recursive=False)
    
    print(f"🔍 Obserwuję folder: {watcher.watch_folder}")
    print("Umieść pliki PDF w tym folderze aby je przetworzyć automatycznie")
    print("Naciśnij Ctrl+C aby zatrzymać")
    
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n🛑 Zatrzymano obserwatora")
    
    observer.join()

if __name__ == "__main__":
    # Zainstaluj wymagane pakiety: pip install watchdog
    start_pdf_watcher()
```

### Przykład 2: Cron job dla regularnego przetwarzania

```bash
#!/bin/bash
# cron_processor.sh - Skrypt dla cron job

# Konfiguracja
DOCUMENTS_DIR="/home/user/documents/to_process"
OUTPUT_DIR="/home/user/documents/processed"
LOG_FILE="/home/user/logs/cron_ocr.log"
LOCK_FILE="/tmp/pdf_ocr.lock"

# Funkcja logowania
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# Sprawdź czy już nie działa
if [ -f "$LOCK_FILE" ]; then
    log "⚠️ Proces już działa (lock file exists)"
    exit 1
fi

# Stwórz lock file
echo $$ > "$LOCK_FILE"
trap "rm -f $LOCK_FILE" EXIT

log "🚀 Rozpoczynam przetwarzanie cron job"

# Sprawdź czy są pliki do przetworzenia
PDF_COUNT=$(find "$DOCUMENTS_DIR" -name "*.pdf" | wc -l)

if [ "$PDF_COUNT" -eq 0 ]; then
    log "ℹ️ Brak plików PDF do przetworzenia"
    exit 0
fi

log "📄 Znaleziono $PDF_COUNT plików PDF"

# Aktywuj środowisko wirtualne
source /home/user/pdf-ocr-processor/venv/bin/activate

# Przejdź do katalogu projektu
cd /home/user/pdf-ocr-processor

# Uruchom przetwarzanie
python pdf_processor.py \
    --documents "$DOCUMENTS_DIR" \
    --output "$OUTPUT_DIR" \
    --model llava:7b \
    --workers 4 >> "$LOG_FILE" 2>&1

if [ $? -eq 0 ]; then
    log "✅ Przetwarzanie zakończone sukcesem"
    
    # Przenieś przetworzone pliki do archiwum
    ARCHIVE_DIR="/home/user/documents/archive/$(date +%Y%m%d)"
    mkdir -p "$ARCHIVE_DIR"
    mv "$DOCUMENTS_DIR"/*.pdf "$ARCHIVE_DIR/" 2>/dev/null
    
    log "📁 Pliki przeniesione do archiwum: $ARCHIVE_DIR"
else
    log "❌ Błąd podczas przetwarzania"
fi

log "🏁 Cron job zakończony"

# Dodaj do crontab:
# # Przetwarzaj PDFy codziennie o 2:00
# 0 2 * * * /home/user/pdf-ocr-processor/cron_processor.sh
#
# # Przetwarzaj co godzinę w godzinach pracy
# 0 9-17 * * 1-5 /home/user/pdf-ocr-processor/cron_processor.sh
```

---

## 🔌 Integracje zewnętrzne

### Przykład 1: Integracja z bazą danych

```python
#!/usr/bin/env python3
"""
Integracja PDF OCR Processor z bazą danych
"""

import sqlite3
import json
from datetime import datetime
from pdf_processor import PDFOCRProcessor
from pathlib import Path

class OCRDatabase:
    def __init__(self, db_path="ocr_results.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Inicjalizuj bazę danych"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela dokumentów
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_size INTEGER,
                page_count INTEGER,
                processing_time REAL,
                average_confidence REAL,
                total_text_length INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(file_path)
            )
        ''')
        
        # Tabela stron
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER,
                page_number INTEGER,
                text TEXT,
                confidence REAL,
                language TEXT,
                image_path TEXT,
                FOREIGN KEY (document_id) REFERENCES documents (id)
            )
        ''')
        
        # Tabela bloków tekstu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS text_blocks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                page_id INTEGER,
                text TEXT,
                bbox_x REAL,
                bbox_y REAL,
                bbox_width REAL,
                bbox_height REAL,
                confidence REAL,
                FOREIGN KEY (page_id) REFERENCES pages (id)
            )
        ''')
        
        # Indeksy dla szybszego wyszukiwania
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_documents_filename ON documents(filename)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_pages_text ON pages(text)')
        
        conn.commit()
        conn.close()
    
    def save_ocr_result(self, pdf_path, ocr_result):
        """Zapisz wynik OCR do bazy danych"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Zapisz dokument
            file_path = Path(pdf_path)
            cursor.execute('''
                INSERT OR REPLACE INTO documents 
                (filename, file_path, file_size, page_count, processing_time, 
                 average_confidence, total_text_length)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                file_path.name,
                str(file_path),
                file_path.stat().st_size if file_path.exists() else 0,
                ocr_result.get("page_count", 0),
                ocr_result.get("processing_time", 0),
                ocr_result.get("average_confidence", 0),
                ocr_result.get("total_text_length", 0)
            ))
            
            document_id = cursor.lastrowid
            
            # Zapisz strony
            for i, page_ocr in enumerate(ocr_result.get("ocr_results", [])):
                cursor.execute('''
                    INSERT INTO pages 
                    (document_id, page_number, text, confidence, language, image_path)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    document_id,
                    i + 1,
                    page_ocr.get("text", ""),
                    page_ocr.get("confidence", 0),
                    page_ocr.get("language", "unknown"),
                    ocr_result.get("image_paths", [None])[i] if i < len(ocr_result.get("image_paths", [])) else None
                ))
                
                page_id = cursor.lastrowid
                
                # Zapisz bloki tekstu
                for block in page_ocr.get("blocks", []):
                    if "bbox" in block and len(block["bbox"]) >= 4:
                        cursor.execute('''
                            INSERT INTO text_blocks 
                            (page_id, text, bbox_x, bbox_y, bbox_width, bbox_height, confidence)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            page_id,
                            block.get("text", ""),
                            block["bbox"][0],
                            block["bbox"][1], 
                            block["bbox"][2],
                            block["bbox"][3],
                            block.get("confidence", 0)
                        ))
            
            conn.commit()
            return document_id
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def search_text(self, query, min_confidence=0.7):
        """Wyszukaj tekst w bazie danych"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT d.filename, p.page_number, p.text, p.confidence
            FROM documents d
            JOIN pages p ON d.id = p.document_id
            WHERE p.text LIKE ? AND p.confidence >= ?
            ORDER BY p.confidence DESC
        ''', (f'%{query}%', min_confidence))
        
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                "filename": row[0],
                "page": row[1],
                "text": row[2],
                "confidence": row[3]
            }
            for row in results
        ]
    
    def get_document_stats(self):
        """Pobierz statystyki dokumentów"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                COUNT(*) as total_documents,
                SUM(page_count) as total_pages,
                AVG(average_confidence) as avg_confidence,
                SUM(total_text_length) as total_text_length,
                AVG(processing_time) as avg_processing_time
            FROM documents
        ''')
        
        row = cursor.fetchone()
        conn.close()
        
        return {
            "total_documents": row[0],
            "total_pages": row[1], 
            "average_confidence": row[2],
            "total_text_length": row[3],
            "average_processing_time": row[4]
        }

# Przykład użycia
def process_with_database():
    """Przetwarzaj PDFy i zapisuj do bazy danych"""
    processor = PDFOCRProcessor()
    db = OCRDatabase()
    
    # Przetwórz wszystkie PDFy
    results = processor.process_all_pdfs()
    
    # Zapisz do bazy danych
    for result in results:
        if "error" not in result:
            document_id = db.save_ocr_result(result["pdf_path"], result)
            print(f"✅ Zapisano do DB: {result['pdf_path']} (ID: {document_id})")
    
    # Pokaż statystyki
    stats = db.get_document_stats()
    print(f"\n📊 Statystyki bazy danych:")
    print(f"  Dokumenty: {stats['total_documents']}")
    print(f"  Strony: {stats['total_pages']}")
    print(f"  Średnia pewność: {stats['average_confidence']:.2%}")
    
    # Przykład wyszukiwania
    search_results = db.search_text("faktura")
    print(f"\n🔍 Znaleziono 'faktura' w {len(search_results)} miejscach")

if __name__ == "__main__":
    process_with_database()
```

### Przykład 2: Webhook do powiadomień

```python
#!/usr/bin/env python3
"""
Webhook do powiadomień o zakończeniu przetwarzania
"""

import requests
import json
from pdf_processor import PDFOCRProcessor

class WebhookNotifier:
    def __init__(self, webhook_url=None, slack_url=None, discord_url=None):
        self.webhook_url = webhook_url
        self.slack_url = slack_url
        self.discord_url = discord_url
    
    def send_slack_notification(self, message, color="good"):
        """Wyślij powiadomienie do Slack"""
        if not self.slack_url:
            return
        
        payload = {
            "attachments": [
                {
                    "color": color,
                    "fields": [
                        {
                            "title": "PDF OCR Processor",
                            "value": message,
                            "short": False
                        }
                    ]
                }
            ]
        }
        
        try:
            response = requests.post(self.slack_url, json=payload)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"❌ Błąd Slack webhook: {e}")
    
    def send_discord_notification(self, message):
        """Wyślij powiadomienie do Discord"""
        if not self.discord_url:
            return
        
        payload = {
            "content": f"🤖 **PDF OCR Processor**\n{message}"
        }
        
        try:
            response = requests.post(self.discord_url, json=payload)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"❌ Błąd Discord webhook: {e}")
    
    def notify_completion(self, results):
        """Powiadom o zakończeniu przetwarzania"""
        successful = len([r for r in results if "error" not in r])
        failed = len([r for r in results if "error" in r])
        total_pages = sum(r.get("page_count", 0) for r in results if "error" not in r)
        
        message = f"""
📄 Przetworzono {successful}/{len(results)} dokumentów
📋 Łącznie {total_pages} stron
{'✅ Wszystko OK' if failed == 0 else f'⚠️ {failed} błędów'}
        """.strip()
        
        color = "good" if failed == 0 else "warning"
        
        self.send_slack_notification(message, color)
        self.send_discord_notification(message)
        
        if self.webhook_url:
            # Webhook generyczny
            payload = {
                "event": "processing_completed",
                "timestamp": json.dumps(results, default=str),
                "summary": {
                    "total_documents": len(results),
                    "successful": successful,
                    "failed": failed,
                    "total_pages": total_pages
                }
            }
            
            try:
                requests.post(self.webhook_url, json=payload)
            except requests.RequestException as e:
                print(f"❌ Błąd webhook: {e}")

# Przykład użycia
def process_with_notifications():
    """Przetwarzanie z powiadomieniami"""
    # Konfiguracja (ustaw swoje URL)
    notifier = WebhookNotifier(
        slack_url="https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK",
        discord_url="https://discord.com/api/webhooks/YOUR/DISCORD/WEBHOOK"
    )
    
    processor = PDFOCRProcessor()
    
    # Powiadom o rozpoczęciu
    notifier.send_slack_notification("🚀 Rozpoczynam przetwarzanie dokumentów PDF", "good")
    
    # Przetwórz
    results = processor.process_all_pdfs()
    
    # Powiadom o zakończeniu
    notifier.notify_completion(results)

if __name__ == "__main__":
    process_with_notifications()
```

---

## ⚡ Optymalizacja wydajności

### Przykład 1: Profile wydajności

```python
#!/usr/bin/env python3
"""
Profiling wydajności PDF OCR Processor
"""

import cProfile
import pstats
import io
from pdf_processor import PDFOCRProcessor
import time
import psutil
import os

class PerformanceProfiler:
    def __init__(self):
        self.processor = PDFOCRProcessor()
        self.start_memory = None
        self.start_time = None
    
    def start_monitoring(self):
        """Rozpocznij monitorowanie"""
        self.start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        self.start_time = time.time()
    
    def stop_monitoring(self):
        """Zatrzymaj monitorowanie i zwróć statystyki"""
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        end_time = time.time()
        
        return {
            "processing_time": end_time - self.start_time,
            "memory_usage": end_memory - self.start_memory,
            "peak_memory": end_memory,
            "cpu_percent": psutil.Process().cpu_percent()
        }
    
    def profile_single_pdf(self, pdf_path):
        """Profiluj przetwarzanie pojedynczego PDF"""
        print(f"🔍 Profilowanie: {pdf_path}")
        
        # Przygotuj profiler
        pr = cProfile.Profile()
        
        # Rozpocznij monitoring
        self.start_monitoring()
        
        # Uruchom z profilem
        pr.enable()
        result = self.processor.process_pdf(pdf_path)
        pr.disable()
        
        # Zatrzymaj monitoring
        stats = self.stop_monitoring()
        
        # Wyniki profilingu
        s = io.StringIO()
        ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
        ps.print_stats(20)  # Top 20 funkcji
        
        profile_text = s.getvalue()
        
        return {
            "ocr_result": result,
            "performance_stats": stats,
            "profile_text": profile_text
        }
    
    def benchmark_models(self, pdf_path, models=["llava:7b", "llama3.2-vision"]):
        """Porównaj wydajność różnych modeli"""
        results = {}
        
        for model in models:
            print(f"🔄 Testowanie modelu: {model}")
            
            self.start_monitoring()
            start = time.time()
            
            result = self.processor.process_pdf(pdf_path, model)
            
            end = time.time()
            stats = self.stop_monitoring()
            
            if "error" not in result:
                results[model] = {
                    "processing_time": end - start,
                    "memory_usage": stats["memory_usage"],
                    "confidence": result.get("average_confidence", 0),
                    "pages": result.get("page_count", 0)
                }
            else:
                results[model] = {"error": result["error"]}
        
        return results
    
    def benchmark_workers(self, pdf_path, worker_counts=[1, 2, 4, 8]):
        """Test różnej liczby workerów"""
        results = {}
        
        for workers in worker_counts:
            print(f"🔄 Testowanie {workers} workerów")
            
            # Ustaw liczbę workerów
            self.processor.max_workers = workers
            
            self.start_monitoring()
            start = time.time()
            
            result = self.processor.process_pdf(pdf_path)
            
            end = time.time()
            stats = self.stop_monitoring()
            
            if "error" not in result:
                results[workers] = {
                    "processing_time": end - start,
                    "memory_usage": stats["memory_usage"],
                    "pages_per_second": result.get("page_count", 0) / (end - start)
                }
        
        return results

# Przykład użycia
def run_performance_tests():
    """Uruchom testy wydajności"""
    profiler = PerformanceProfiler()
    
    # Znajdź testowy PDF
    test_pdf = "documents/test.pdf"
    
    if not os.path.exists(test_pdf):
        print("❌ Brak pliku testowego: documents/test.pdf")
        return
    
    print("🚀 Rozpoczynam testy wydajności")
    print("=" * 50)
    
    # Test pojedynczego PDF z profilingiem
    profile_result = profiler.profile_single_pdf(test_pdf)
    
    print(f"📊 Wyniki profilingu:")
    print(f"  Czas: {profile_result['performance_stats']['processing_time']:.2f}s")
    print(f"  Pamięć: {profile_result['performance_stats']['memory_usage']:.1f}MB")
    print(f"  Peak pamięci: {profile_result['performance_stats']['peak_memory']:.1f}MB")
    
    # Zapisz szczegółowy profiling
    with open("performance_profile.txt", "w") as f:
        f.write(profile_result['profile_text'])
    
    # Benchmark modeli
    print(f"\n🤖 Porównanie modeli:")
    model_results = profiler.benchmark_models(test_pdf)
    
    for model, stats in model_results.items():
        if "error" not in stats:
            print(f"  {model}:")
            print(f"    Czas: {stats['processing_time']:.2f}s")
            print(f"    Pamięć: {stats['memory_usage']:.1f}MB") 
            print(f"    Pewność: {stats['confidence']:.2%}")
        else:
            print(f"  {model}: {stats['error']}")
    
    # Benchmark workerów
    print(f"\n⚡ Porównanie liczby workerów:")
    worker_results = profiler.benchmark_workers(test_pdf)
    
    for workers, stats in worker_results.items():
        print(f"  {workers} workerów:")
        print(f"    Czas: {stats['processing_time']:.2f}s")
        print(f"    Pamięć: {stats['memory_usage']:.1f}MB")
        print(f"    Strony/s: {stats['pages_per_second']:.2f}")
    
    print(f"\n💾 Szczegółowy profiling zapisany: performance_profile.txt")

if __name__ == "__main__":
    # Wymaga: pip install psutil
    run_performance_tests()
```

---

## 📝 Podsumowanie

Te przykłady pokazują szerokie możliwości zastosowania PDF OCR Processor:

- **Podstawowe użycie** - szybki start z przetwarzaniem dokumentów
- **Integracja Python** - wbudowanie w własne aplikacje
- **Batch processing** - masowe przetwarzanie z kategoryzacją
- **Analiza wyników** - statystyki, wykresy, dashboard
- **Automatyzacja** - watch folder, cron jobs
- **Integracje** - bazy danych, webhooks, powiadomienia
- **Optymalizacja** - profiling, benchmarki, tuning wydajności

Każdy przykład można dostosować do własnych potrzeb i zintegrować z istniejącymi systemami.

---

*Ostatnia aktualizacja: 15 stycznia 2025*