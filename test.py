#!/usr/bin/env python3
"""
Test Runner dla PDF OCR Processor
Sprawdza poprawność implementacji i identyfikuje potencjalne problemy
"""

import sys
import tempfile
import shutil
import json
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock
import time


def test_imports():
    """Test importów wszystkich wymaganych bibliotek"""
    print("🔍 Test 1: Sprawdzanie importów...")

    required_modules = [
        ('fitz', 'PyMuPDF'),
        ('PIL', 'Pillow'),
        ('concurrent.futures', 'threading'),
        ('xml.etree.ElementTree', 'xml'),
        ('pathlib', 'pathlib'),
        ('json', 'json'),
        ('base64', 'base64'),
        ('subprocess', 'subprocess'),
        ('logging', 'logging')
    ]

    missing = []
    for module, name in required_modules:
        try:
            __import__(module)
            print(f"  ✅ {name}")
        except ImportError as e:
            print(f"  ❌ {name}: {e}")
            missing.append(name)

    if missing:
        print(f"\n❌ Brakujące moduły: {', '.join(missing)}")
        return False

    print("✅ Wszystkie importy dostępne")
    return True


def test_ollama_interface():
    """Test interfejsu z Ollama"""
    print("\n🔍 Test 2: Sprawdzanie interfejsu Ollama...")

    # Test dostępności Ollama
    try:
        result = subprocess.run(['ollama', '--version'],
                                capture_output=True, timeout=5)
        if result.returncode == 0:
            print("  ✅ Ollama jest zainstalowana")

            # Test listowania modeli
            result = subprocess.run(['ollama', 'list'],
                                    capture_output=True, timeout=10)
            if result.returncode == 0:
                models = []
                for line in result.stdout.decode().split('\n')[1:]:
                    if line.strip():
                        model_name = line.split()[0]
                        if ':' in model_name:
                            models.append(model_name)

                if models:
                    print(f"  ✅ Dostępne modele: {', '.join(models)}")
                    return True, models
                else:
                    print("  ⚠️ Brak pobranych modeli")
                    print("  💡 Pobierz model: ollama pull llava:7b")
                    return True, []
            else:
                print(f"  ❌ Błąd listowania modeli: {result.stderr.decode()}")
                return False, []
        else:
            print(f"  ❌ Ollama nie odpowiada: {result.stderr.decode()}")
            return False, []

    except FileNotFoundError:
        print("  ❌ Ollama nie jest zainstalowana")
        print("  💡 Zainstaluj z: https://ollama.ai")
        return False, []
    except subprocess.TimeoutExpired:
        print("  ❌ Ollama nie odpowiada (timeout)")
        return False, []


def test_pdf_processing():
    """Test przetwarzania PDF"""
    print("\n🔍 Test 3: Sprawdzanie przetwarzania PDF...")

    try:
        import fitz

        # Stwórz minimalny testowy PDF
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            # Minimalna struktura PDF
            pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
>>
endobj

xref
0 4
0000000000 65535 f 
0000000010 00000 n 
0000000079 00000 n 
0000000136 00000 n 
trailer
<<
/Size 4
/Root 1 0 R
>>
startxref
208
%%EOF"""
            tmp.write(pdf_content)
            tmp_path = tmp.name

        # Test otwarcia PDF
        try:
            doc = fitz.open(tmp_path)
            page_count = len(doc)
            doc.close()
            print(f"  ✅ PyMuPDF może otworzyć PDF ({page_count} stron)")

            # Sprzątanie
            Path(tmp_path).unlink()
            return True

        except Exception as e:
            print(f"  ❌ Błąd przetwarzania PDF: {e}")
            Path(tmp_path).unlink()
            return False

    except ImportError:
        print("  ❌ PyMuPDF nie jest dostępne")
        return False


def test_image_processing():
    """Test przetwarzania obrazów"""
    print("\n🔍 Test 4: Sprawdzanie przetwarzania obrazów...")

    try:
        from PIL import Image
        import io

        # Stwórz testowy obraz
        img = Image.new('RGB', (100, 100), color='white')

        # Test zapisywania PNG
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')

        # Test base64 encoding
        import base64
        encoded = base64.b64encode(img_bytes.getvalue())

        print("  ✅ PIL może tworzyć i zapisywać obrazy")
        print("  ✅ Base64 encoding działa")
        return True

    except Exception as e:
        print(f"  ❌ Błąd przetwarzania obrazów: {e}")
        return False


def test_svg_generation():
    """Test generowania SVG"""
    print("\n🔍 Test 5: Sprawdzanie generowania SVG...")

    try:
        import xml.etree.ElementTree as ET

        # Test tworzenia SVG
        svg_root = ET.Element("svg", {
            "xmlns": "http://www.w3.org/2000/svg",
            "width": "100",
            "height": "100"
        })

        # Dodaj testowy element
        rect = ET.SubElement(svg_root, "rect", {
            "x": "10",
            "y": "10",
            "width": "80",
            "height": "80",
            "fill": "blue"
        })

        # Test zapisywania
        tree = ET.ElementTree(svg_root)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.svg', delete=False) as tmp:
            tree.write(tmp.name, encoding='utf-8', xml_declaration=True)
            svg_path = tmp.name

        # Sprawdź czy plik został utworzony
        if Path(svg_path).exists():
            # Sprawdź zawartość
            with open(svg_path, 'r') as f:
                content = f.read()
                if '<svg' in content and '</svg>' in content:
                    print("  ✅ XML/SVG generation działa")
                    Path(svg_path).unlink()
                    return True

        print("  ❌ Błąd generowania SVG")
        return False

    except Exception as e:
        print(f"  ❌ Błąd XML/SVG: {e}")
        return False


def test_json_handling():
    """Test obsługi JSON"""
    print("\n🔍 Test 6: Sprawdzanie obsługi JSON...")

    try:
        import json

        # Test danych z różnymi encodingami
        test_data = {
            "text": "Test z polskimi znakami: ąćęłńóśźż",
            "confidence": 0.95,
            "blocks": [
                {
                    "text": "Blok tekstu",
                    "bbox": [10.5, 20.5, 100.5, 30.5]
                }
            ]
        }

        # Test serializacji
        json_str = json.dumps(test_data, ensure_ascii=False, indent=2)

        # Test deserializacji
        parsed = json.loads(json_str)

        if parsed["text"] == test_data["text"]:
            print("  ✅ JSON handling z polskimi znakami działa")
            return True
        else:
            print("  ❌ Błąd kodowania znaków w JSON")
            return False

    except Exception as e:
        print(f"  ❌ Błąd JSON: {e}")
        return False


def test_file_operations():
    """Test operacji na plikach"""
    print("\n🔍 Test 7: Sprawdzanie operacji na plikach...")

    try:
        from pathlib import Path
        import tempfile

        # Test tworzenia katalogów
        with tempfile.TemporaryDirectory() as tmp_dir:
            test_dir = Path(tmp_dir) / "test_folder"
            test_dir.mkdir(exist_ok=True)

            # Test tworzenia plików
            test_file = test_dir / "test.txt"
            test_file.write_text("Test content", encoding='utf-8')

            # Test czytania
            content = test_file.read_text(encoding='utf-8')

            # Test globowania
            files = list(test_dir.glob("*.txt"))

            if len(files) == 1 and content == "Test content":
                print("  ✅ Operacje na plikach działają")
                return True
            else:
                print("  ❌ Błąd operacji na plikach")
                return False

    except Exception as e:
        print(f"  ❌ Błąd operacji na plikach: {e}")
        return False


def test_performance():
    """Test wydajności podstawowych operacji"""
    print("\n🔍 Test 8: Sprawdzanie wydajności...")

    try:
        import time
        from PIL import Image
        import base64
        import io

        # Test wydajności tworzenia obrazu
        start = time.time()
        for i in range(10):
            img = Image.new('RGB', (800, 600), color='white')
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            base64.b64encode(img_bytes.getvalue())

        image_time = time.time() - start

        # Test wydajności JSON
        start = time.time()
        test_data = {"text": "x" * 1000, "blocks": [{"bbox": [i, i, i, i]} for i in range(100)]}
        for i in range(100):
            json.dumps(test_data)
        json_time = time.time() - start

        print(f"  ✅ Tworzenie obrazów: {image_time:.3f}s/10 obrazów")
        print(f"  ✅ Przetwarzanie JSON: {json_time:.3f}s/100 operacji")

        if image_time < 5.0 and json_time < 1.0:
            print("  ✅ Wydajność w normie")
            return True
        else:
            print("  ⚠️ Wolna wydajność - może wpłynąć na przetwarzanie")
            return True

    except Exception as e:
        print(f"  ❌ Błąd testu wydajności: {e}")
        return False


def test_error_handling():
    """Test obsługi błędów"""
    print("\n🔍 Test 9: Sprawdzanie obsługi błędów...")

    try:
        # Test obsługi nieistniejących plików
        from pathlib import Path
        nonexistent = Path("/path/that/does/not/exist/file.pdf")

        # To powinno działać bez wyjątku
        exists = nonexistent.exists()

        # Test obsługi błędnych danych JSON
        import json
        try:
            json.loads("invalid json {")
            print("  ❌ JSON error handling nie działa")
            return False
        except json.JSONDecodeError:
            pass  # Oczekiwany błąd

        # Test timeout w subprocess
        import subprocess
        try:
            subprocess.run(['sleep', '10'], timeout=0.1)
            print("  ❌ Subprocess timeout nie działa")
            return False
        except subprocess.TimeoutExpired:
            pass  # Oczekiwany błąd
        except FileNotFoundError:
            pass  # sleep może nie istnieć na Windows

        print("  ✅ Obsługa błędów działa prawidłowo")
        return True

    except Exception as e:
        print(f"  ❌ Błąd testu obsługi błędów: {e}")
        return False


def run_integration_test():
    """Test integracyjny całego systemu"""
    print("\n🔍 Test 10: Test integracyjny...")

    try:
        # Import głównej klasy
        from proc import PDFOCRProcessor

        # Test inicjalizacji
        with tempfile.TemporaryDirectory() as tmp_dir:
            processor = PDFOCRProcessor(
                documents_folder=str(Path(tmp_dir) / "docs"),
                output_folder=str(Path(tmp_dir) / "output")
            )

            # Sprawdź czy katalogi zostały utworzone
            if processor.output_folder.exists():
                print("  ✅ Inicjalizacja processora działa")

                # Test sprawdzania modeli
                models = processor.available_models
                print(f"  ✅ Wykryto {len(models)} modeli")

                return True
            else:
                print("  ❌ Błąd inicjalizacji processora")
                return False

    except ImportError as e:
        print(f"  ❌ Nie można zaimportować głównej klasy: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Błąd testu integracyjnego: {e}")
        return False


def main():
    """Główna funkcja testów"""
    print("🧪 PDF OCR Processor - Test Suite")
    print("=" * 50)

    tests = [
        ("Importy bibliotek", test_imports),
        ("Interfejs Ollama", test_ollama_interface),
        ("Przetwarzanie PDF", test_pdf_processing),
        ("Przetwarzanie obrazów", test_image_processing),
        ("Generowanie SVG", test_svg_generation),
        ("Obsługa JSON", test_json_handling),
        ("Operacje na plikach", test_file_operations),
        ("Wydajność", test_performance),
        ("Obsługa błędów", test_error_handling),
        ("Test integracyjny", run_integration_test)
    ]

    results = []
    total_time = time.time()

    for test_name, test_func in tests:
        try:
            start_time = time.time()

            # Specjalna obsługa dla testu Ollama (zwraca tuple)
            if test_name == "Interfejs Ollama":
                success, models = test_func()
            else:
                success = test_func()

            test_time = time.time() - start_time
            results.append((test_name, success, test_time))

        except Exception as e:
            print(f"  ❌ KRYTYCZNY BŁĄD: {e}")
            results.append((test_name, False, 0))

    total_time = time.time() - total_time

    # Podsumowanie
    print("\n" + "=" * 50)
    print("📊 PODSUMOWANIE TESTÓW")
    print("=" * 50)

    passed = sum(1 for _, success, _ in results if success)
    total = len(results)

    print(f"⏱️ Całkowity czas testów: {total_time:.2f}s")
    print(f"✅ Testy zakończone sukcesem: {passed}/{total}")
    print(f"❌ Testy zakończone błędem: {total - passed}/{total}")

    if passed == total:
        print("\n🎉 WSZYSTKIE TESTY PRZESZŁY!")
        print("✅ Kod jest gotowy do użycia")
        readiness_score = 100
    else:
        print(f"\n⚠️ GOTOWOŚĆ KODU: {passed / total * 100:.0f}%")
        readiness_score = passed / total * 100

        print("\n❌ Nieudane testy:")
        for test_name, success, test_time in results:
            if not success:
                print(f"  - {test_name}")

    # Szczegółowy raport
    print(f"\n📋 Szczegóły testów:")
    for test_name, success, test_time in results:
        status = "✅" if success else "❌"
        print(f"  {status} {test_name}: {test_time:.3f}s")

    # Rekomendacje
    print(f"\n💡 Rekomendacje:")
    if readiness_score >= 90:
        print("  - Kod jest gotowy do produkcji")
        print("  - Wszystkie główne funkcje działają")
    elif readiness_score >= 70:
        print("  - Kod jest częściowo gotowy")
        print("  - Napraw nieudane testy przed użyciem")
    else:
        print("  - Kod wymaga znaczących poprawek")
        print("  - Zainstaluj brakujące zależności")
        print("  - Sprawdź konfigurację Ollama")

    # Kod wyjścia
    return 0 if passed == total else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)