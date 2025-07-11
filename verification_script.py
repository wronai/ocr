#!/usr/bin/env python3
"""
PDF OCR Processor - Skrypt weryfikacyjny instalacji
Kompleksowo sprawdza czy wszystkie komponenty działają poprawnie
"""

import sys
import os
import subprocess
import tempfile
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Tuple

# Kolory dla terminala
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header():
    """Wyświetla nagłówek programu"""
    print(f"{Colors.PURPLE}{Colors.BOLD}")
    print("=" * 60)
    print("🔍 PDF OCR Processor - Weryfikacja instalacji v2.0")
    print("=" * 60)
    print(f"{Colors.END}")

def print_success(msg: str):
    """Wyświetla wiadomość sukcesu"""
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")

def print_error(msg: str):
    """Wyświetla wiadomość błędu"""
    print(f"{Colors.RED}❌ {msg}{Colors.END}")

def print_warning(msg: str):
    """Wyświetla ostrzeżenie"""
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.END}")

def print_info(msg: str):
    """Wyświetla informację"""
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.END}")

def print_step(msg: str):
    """Wyświetla krok weryfikacji"""
    print(f"\n{Colors.CYAN}{Colors.BOLD}📋 {msg}{Colors.END}")

class InstallationVerifier:
    """Klasa do weryfikacji instalacji"""
    
    def __init__(self):
        self.results = []
        self.start_time = time.time()
    
    def add_result(self, test_name: str, success: bool, details: str = "", 
                   suggestion: str = ""):
        """Dodaje wynik testu"""
        self.results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "suggestion": suggestion,
            "timestamp": time.time()
        })
    
    def check_python_version(self) -> bool:
        """Sprawdza wersję Pythona"""
        print_step("Sprawdzanie wersji Pythona")
        
        version = sys.version_info
        version_str = f"{version.major}.{version.minor}.{version.micro}"
        
        if version.major == 3 and version.minor >= 8:
            print_success(f"Python {version_str} ✓")
            self.add_result("Python Version", True, version_str)
            return True
        else:
            print_error(f"Python {version_str} - wymagany 3.8+")
            self.add_result("Python Version", False, version_str, 
                          "Zainstaluj Python 3.8 lub nowszy")
            return False
    
    def check_python_packages(self) -> bool:
        """Sprawdza pakiety Pythona"""
        print_step("Sprawdzanie pakietów Pythona")
        
        required_packages = [
            ("fitz", "PyMuPDF"),
            ("PIL", "Pillow"),
            ("yaml", "PyYAML"),
            ("pathlib", "pathlib"),
            ("concurrent.futures", "concurrent.futures"),
            ("xml.etree.ElementTree", "xml"),
            ("json", "json"),
            ("base64", "base64")
        ]
        
        missing_packages = []
        
        for module, package_name in required_packages:
            try:
                __import__(module)
                print_success(f"{package_name} ✓")
            except ImportError as e:
                print_error(f"{package_name} - {e}")
                missing_packages.append(package_name)
        
        if not missing_packages:
            self.add_result("Python Packages", True, 
                          f"Wszystkie {len(required_packages)} pakietów zainstalowanych")
            return True
        else:
            self.add_result("Python Packages", False, 
                          f"Brak pakietów: {', '.join(missing_packages)}",
                          f"pip install {' '.join(missing_packages)}")
            return False
    
    def check_ollama_installation(self) -> Tuple[bool, List[str]]:
        """Sprawdza instalację Ollama"""
        print_step("Sprawdzanie instalacji Ollama")
        
        try:
            # Sprawdź czy ollama command istnieje
            result = subprocess.run(['ollama', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                version = result.stdout.strip()
                print_success(f"Ollama {version} ✓")
                
                # Sprawdź dostępne modele
                models_result = subprocess.run(['ollama', 'list'], 
                                             capture_output=True, text=True, timeout=10)
                
                if models_result.returncode == 0:
                    models = []
                    for line in models_result.stdout.split('\n')[1:]:
                        if line.strip() and not line.startswith('NAME'):
                            model_name = line.split()[0]
                            if ':' in model_name:
                                models.append(model_name)
                    
                    if models:
                        print_success(f"Dostępne modele: {', '.join(models)}")
                        self.add_result("Ollama Installation", True, 
                                      f"Version: {version}, Models: {len(models)}")
                        return True, models
                    else:
                        print_warning("Ollama zainstalowana, ale brak modeli")
                        self.add_result("Ollama Installation", False, 
                                      "Brak pobranych modeli",
                                      "ollama pull llava:7b")
                        return False, []
                else:
                    print_error("Ollama nie odpowiada na 'list' command")
                    self.add_result("Ollama Installation", False, 
                                  "Błąd komunikacji z Ollama")
                    return False, []
            else:
                print_error("Ollama command failed")
                self.add_result("Ollama Installation", False, 
                              "Ollama nie odpowiada")
                return False, []
                
        except FileNotFoundError:
            print_error("Ollama nie jest zainstalowana")
            self.add_result("Ollama Installation", False, 
                          "Ollama nie znaleziona",
                          "Zainstaluj z https://ollama.ai")
            return False, []
        except subprocess.TimeoutExpired:
            print_error("Ollama timeout")
            self.add_result("Ollama Installation", False, 
                          "Timeout podczas sprawdzania Ollama")
            return False, []
    
    def check_ollama_service(self) -> bool:
        """Sprawdza czy serwis Ollama działa"""
        print_step("Sprawdzanie serwisu Ollama")
        
        try:
            result = subprocess.run(['ollama', 'ps'], 
                                  capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                print_success("Serwis Ollama działa ✓")
                self.add_result("Ollama Service", True, "Serwis aktywny")
                return True
            else:
                print_warning("Serwis Ollama może nie działać")
                self.add_result("Ollama Service", False, 
                              "Serwis nie odpowiada",
                              "ollama serve")
                return False
                
        except Exception as e:
            print_error(f"Błąd sprawdzania serwisu: {e}")
            self.add_result("Ollama Service", False, str(e))
            return False
    
    def test_pdf_processing(self) -> bool:
        """Test przetwarzania PDF"""
        print_step("Test przetwarzania PDF")
        
        try:
            import fitz
            
            # Stwórz minimalny test PDF
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
                # Minimal valid PDF
                pdf_content = b"""%PDF-1.4
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
                tmp.write(pdf_content)
                tmp_path = tmp.name
            
            # Test PyMuPDF
            doc = fitz.open(tmp_path)
            page_count = len(doc)
            doc.close()
            
            # Cleanup
            os.unlink(tmp_path)
            
            print_success(f"PyMuPDF może przetwarzać PDF ({page_count} strona)")
            self.add_result("PDF Processing", True, 
                          f"PyMuPDF działa, test PDF: {page_count} strona")
            return True
            
        except Exception as e:
            print_error(f"Błąd przetwarzania PDF: {e}")
            self.add_result("PDF Processing", False, str(e),
                          "pip install PyMuPDF")
            return False
    
    def test_image_processing(self) -> bool:
        """Test przetwarzania obrazów"""
        print_step("Test przetwarzania obrazów")
        
        try:
            from PIL import Image
            import io
            import base64
            
            # Stwórz testowy obraz
            img = Image.new('RGB', (100, 100), color='white')
            
            # Test zapisywania do bytes
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            
            # Test base64 encoding
            encoded = base64.b64encode(img_bytes.getvalue())
            
            print_success("Pillow i base64 działają ✓")
            self.add_result("Image Processing", True, 
                          "PIL i base64 encoding działają")
            return True
            
        except Exception as e:
            print_error(f"Błąd przetwarzania obrazów: {e}")
            self.add_result("Image Processing", False, str(e),
                          "pip install Pillow")
            return False
    
    def test_svg_generation(self) -> bool:
        """Test generowania SVG"""
        print_step("Test generowania SVG")
        
        try:
            import xml.etree.ElementTree as ET
            
            # Stwórz testowy SVG
            svg_root = ET.Element("svg", {
                "xmlns": "http://www.w3.org/2000/svg",
                "width": "100",
                "height": "100"
            })
            
            rect = ET.SubElement(svg_root, "rect", {
                "x": "10", "y": "10", "width": "80", "height": "80",
                "fill": "blue"
            })
            
            # Test konwersji do stringa
            tree = ET.ElementTree(svg_root)
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.svg', 
                                           delete=True) as tmp:
                tree.write(tmp.name, encoding='utf-8', xml_declaration=True)
                
                # Sprawdź czy plik został utworzony poprawnie
                with open(tmp.name, 'r') as f:
                    content = f.read()
                    if '<svg' in content and '</svg>' in content:
                        print_success("XML/SVG generation działa ✓")
                        self.add_result("SVG Generation", True, 
                                      "XML i SVG generation działają")
                        return True
            
            print_error("SVG nie został poprawnie wygenerowany")
            self.add_result("SVG Generation", False, 
                          "Błąd generowania SVG")
            return False
            
        except Exception as e:
            print_error(f"Błąd generowania SVG: {e}")
            self.add_result("SVG Generation", False, str(e))
            return False
    
    def test_json_handling(self) -> bool:
        """Test obsługi JSON z Unicode"""
        print_step("Test obsługi JSON")
        
        try:
            import json
            
            # Test z polskimi znakami
            test_data = {
                "text": "Test z polskimi znakami: ąćęłńóśźż ĄĆĘŁŃÓŚŹŻ",
                "confidence": 0.95,
                "language": "pl",
                "blocks": [
                    {
                        "text": "Przykładowy tekst",
                        "bbox": [10.5, 20.5, 100.5, 30.5],
                        "confidence": 0.92
                    }
                ]
            }
            
            # Test serializacji
            json_str = json.dumps(test_data, ensure_ascii=False, indent=2)
            
            # Test deserializacji
            parsed = json.loads(json_str)
            
            # Sprawdź czy polskie znaki zostały zachowane
            if parsed["text"] == test_data["text"]:
                print_success("JSON z polskimi znakami działa ✓")
                self.add_result("JSON Handling", True, 
                              "JSON z Unicode/polskimi znakami")
                return True
            else:
                print_error("Błąd kodowania polskich znaków")
                self.add_result("JSON Handling", False, 
                              "Problemy z kodowaniem Unicode")
                return False
                
        except Exception as e:
            print_error(f"Błąd obsługi JSON: {e}")
            self.add_result("JSON Handling", False, str(e))
            return False
    
    def test_file_operations(self) -> bool:
        """Test operacji na plikach"""
        print_step("Test operacji na plikach")
        
        try:
            with tempfile.TemporaryDirectory() as tmp_dir:
                tmp_path = Path(tmp_dir)
                
                # Test tworzenia katalogów
                test_dir = tmp_path / "test_folder"
                test_dir.mkdir(exist_ok=True)
                
                # Test zapisu pliku z polskimi znakami
                test_file = test_dir / "test_ąć.txt"
                test_content = "Test content with Polish: ąćęłńóśźż"
                test_file.write_text(test_content, encoding='utf-8')
                
                # Test czytania
                read_content = test_file.read_text(encoding='utf-8')
                
                # Test globbing
                files = list(test_dir.glob("*.txt"))
                
                if (len(files) == 1 and 
                    read_content == test_content and 
                    test_file.exists()):
                    print_success("Operacje na plikach działają ✓")
                    self.add_result("File Operations", True, 
                                  "Tworzenie, zapis, odczyt, globbing")
                    return True
                else:
                    print_error("Błąd operacji na plikach")
                    self.add_result("File Operations", False, 
                                  "Niepowodzenie podstawowych operacji")
                    return False
                    
        except Exception as e:
            print_error(f"Błąd operacji na plikach: {e}")
            self.add_result("File Operations", False, str(e))
            return False
    
    def test_project_structure(self) -> bool:
        """Test struktury projektu"""
        print_step("Test struktury projektu")
        
        required_items = [
            ("documents", "folder", "Folder na dokumenty PDF"),
            ("output", "folder", "Folder na wyniki"),
            ("config/config.yaml", "file", "Plik konfiguracyjny"),
            ("requirements.txt", "file", "Lista zależności Python"),
            ("README.md", "file", "Dokumentacja projektu")
        ]
        
        missing_items = []
        
        for item, item_type, description in required_items:
            path = Path(item)
            
            if item_type == "folder":
                if path.is_dir():
                    print_success(f"{description} ✓")
                else:
                    print_warning(f"{description} - brak")
                    missing_items.append(item)
            else:  # file
                if path.is_file():
                    print_success(f"{description} ✓")
                else:
                    print_warning(f"{description} - brak")
                    missing_items.append(item)
        
        if not missing_items:
            self.add_result("Project Structure", True, 
                          "Wszystkie wymagane elementy obecne")
            return True
        else:
            self.add_result("Project Structure", False, 
                          f"Brak: {', '.join(missing_items)}",
                          "Uruchom ponownie skrypt instalacyjny")
            return False
    
    def test_main_module_import(self) -> bool:
        """Test importu głównego modułu"""
        print_step("Test importu głównego modułu")
        
        try:
            # Dodaj aktualny katalog do path
            sys.path.insert(0, os.getcwd())
            
            # Próba importu
            from pdf_processor import PDFOCRProcessor
            
            # Test podstawowej inicjalizacji
            with tempfile.TemporaryDirectory() as tmp_dir:
                processor = PDFOCRProcessor(
                    documents_folder=tmp_dir,
                    output_folder=tmp_dir
                )
                
                # Sprawdź czy ma wymagane atrybuty/metody
                required_methods = [
                    'process_pdf',
                    'process_all_pdfs', 
                    'extract_text_with_ollama',
                    'pdf_to_images'
                ]
                
                for method in required_methods:
                    if not hasattr(processor, method):
                        raise AttributeError(f"Brak metody: {method}")
                
            print_success("Import głównego modułu ✓")
            self.add_result("Main Module Import", True, 
                          "PDFOCRProcessor i wszystkie metody dostępne")
            return True
            
        except ImportError as e:
            print_error(f"Błąd importu: {e}")
            self.add_result("Main Module Import", False, 
                          f"ImportError: {e}",
                          "Sprawdź czy pdf_processor.py istnieje")
            return False
        except Exception as e:
            print_error(f"Błąd inicjalizacji: {e}")
            self.add_result("Main Module Import", False, 
                          f"Błąd: {e}")
            return False
    
    def test_performance_basic(self) -> bool:
        """Podstawowy test wydajności"""
        print_step("Test podstawowej wydajności")
        
        try:
            import time
            from PIL import Image
            import io
            import base64
            
            # Test tworzenia i kodowania obrazów
            start_time = time.time()
            
            for i in range(5):
                img = Image.new('RGB', (800, 600), color='white')
                img_bytes = io.BytesIO()
                img.save(img_bytes, format='PNG')
                base64.b64encode(img_bytes.getvalue())
            
            image_time = time.time() - start_time
            
            # Test JSON operations
            start_time = time.time()
            import json
            
            test_data = {
                "text": "Sample text " * 100,
                "blocks": [{"bbox": [i, i, i, i]} for i in range(50)]
            }
            
            for i in range(50):
                json.dumps(test_data)
            
            json_time = time.time() - start_time
            
            print_success(f"Wydajność: obrazy {image_time:.2f}s, JSON {json_time:.2f}s")
            
            if image_time < 10.0 and json_time < 2.0:
                self.add_result("Performance", True, 
                              f"Wydajność OK: img={image_time:.2f}s, json={json_time:.2f}s")
                return True
            else:
                self.add_result("Performance", False, 
                              f"Wolna wydajność: img={image_time:.2f}s, json={json_time:.2f}s",
                              "Sprawdź zasoby systemowe")
                return False
                
        except Exception as e:
            print_error(f"Błąd testu wydajności: {e}")
            self.add_result("Performance", False, str(e))
            return False
    
    def generate_report(self) -> Dict[str, Any]:
        """Generuje raport weryfikacji"""
        total_time = time.time() - self.start_time
        
        successful_tests = sum(1 for r in self.results if r["success"])
        total_tests = len(self.results)
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        report = {
            "verification_timestamp": time.time(),
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "failed_tests": total_tests - successful_tests,
            "success_rate": success_rate,
            "total_time_seconds": total_time,
            "system_info": {
                "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                "platform": sys.platform,
                "cwd": os.getcwd()
            },
            "test_results": self.results
        }
        
        return report
    
    def print_summary(self, report: Dict[str, Any]):
        """Wyświetla podsumowanie weryfikacji"""
        print_step("Podsumowanie weryfikacji")
        
        success_rate = report["success_rate"]
        
        if success_rate == 100:
            print(f"{Colors.GREEN}{Colors.BOLD}")
            print("🎉 INSTALACJA W PEŁNI FUNKCJONALNA!")
            print(f"✅ Wszystkie testy przeszły pomyślnie ({report['successful_tests']}/{report['total_tests']})")
            print("🚀 Aplikacja jest gotowa do użycia")
            
        elif success_rate >= 80:
            print(f"{Colors.YELLOW}{Colors.BOLD}")
            print("⚠️ INSTALACJA CZĘŚCIOWO FUNKCJONALNA")
            print(f"✅ Przeszło: {report['successful_tests']}/{report['total_tests']} testów ({success_rate:.0f}%)")
            print("🔧 Wymaga drobnych poprawek")
            
        else:
            print(f"{Colors.RED}{Colors.BOLD}")
            print("❌ INSTALACJA WYMAGA POPRAWEK")
            print(f"✅ Przeszło: {report['successful_tests']}/{report['total_tests']} testów ({success_rate:.0f}%)")
            print("🚨 Krytyczne problemy do rozwiązania")
        
        print(f"{Colors.END}")
        
        # Pokaż nieudane testy
        failed_tests = [r for r in self.results if not r["success"]]
        if failed_tests:
            print(f"\n{Colors.RED}❌ Nieudane testy:{Colors.END}")
            for test in failed_tests:
                print(f"  • {test['test']}: {test['details']}")
                if test['suggestion']:
                    print(f"    💡 {test['suggestion']}")
        
        print(f"\n{Colors.BLUE}📊 Statystyki:{Colors.END}")
        print(f"  • Czas weryfikacji: {report['total_time_seconds']:.2f}s")
        print(f"  • Python: {report['system_info']['python_version']}")
        print(f"  • Platforma: {report['system_info']['platform']}")
        
        # Następne kroki
        if success_rate == 100:
            print(f"\n{Colors.GREEN}🎯 Następne kroki:{Colors.END}")
            print("  1. Umieść pliki PDF w folderze 'documents/'")
            print("  2. Uruchom: python pdf_processor.py")
            print("  3. Sprawdź wyniki w folderze 'output/'")
        elif success_rate >= 80:
            print(f"\n{Colors.YELLOW}🔧 Zalecane działania:{Colors.END}")
            print("  1. Napraw nieudane testy (patrz powyżej)")
            print("  2. Uruchom weryfikację ponownie")
            print("  3. Jeśli problemy pozostają, sprawdź dokumentację")
        else:
            print(f"\n{Colors.RED}🚨 Wymagane działania:{Colors.END}")
            print("  1. Zainstaluj brakujące zależności")
            print("  2. Uruchom skrypt instalacyjny ponownie")
            print("  3. Sprawdź dokumentację troubleshooting")
    
    def save_report(self, report: Dict[str, Any]):
        """Zapisuje raport do pliku"""
        try:
            os.makedirs("logs", exist_ok=True)
            report_path = "logs/verification_report.json"
            
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            print_info(f"Raport zapisany: {report_path}")
            
        except Exception as e:
            print_warning(f"Nie udało się zapisać raportu: {e}")
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Uruchamia wszystkie testy weryfikacyjne"""
        print_header()
        
        # Lista testów w kolejności
        tests = [
            ("Python Version", self.check_python_version),
            ("Python Packages", self.check_python_packages),
            ("Ollama Installation", lambda: self.check_ollama_installation()[0]),
            ("Ollama Service", self.check_ollama_service),
            ("PDF Processing", self.test_pdf_processing),
            ("Image Processing", self.test_image_processing),
            ("SVG Generation", self.test_svg_generation),
            ("JSON Handling", self.test_json_handling),
            ("File Operations", self.test_file_operations),
            ("Project Structure", self.test_project_structure),
            ("Main Module Import", self.test_main_module_import),
            ("Performance", self.test_performance_basic)
        ]
        
        print_info(f"Uruchamiam {len(tests)} testów weryfikacyjnych...")
        
        # Uruchom wszystkie testy
        for test_name, test_func in tests:
            try:
                test_func()
            except Exception as e:
                print_error(f"Krytyczny błąd w teście '{test_name}': {e}")
                self.add_result(test_name, False, f"Exception: {e}")
        
        # Wygeneruj raport
        report = self.generate_report()
        
        # Wyświetl podsumowanie
        self.print_summary(report)
        
        # Zapisz raport
        self.save_report(report)
        
        return report

def main():
    """Główna funkcja weryfikacji"""
    verifier = InstallationVerifier()
    report = verifier.run_all_tests()
    
    # Kod wyjścia na podstawie wyników
    success_rate = report["success_rate"]
    if success_rate == 100:
        return 0  # Sukces
    elif success_rate >= 80:
        return 1  # Częściowy sukces
    else:
        return 2  # Błąd

if __name__ == "__main__":
    sys.exit(main())
