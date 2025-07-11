#!/usr/bin/env python3
"""
PDF Multi-Page OCR Processor - Poprawiona wersja
Przetwarza wielostronicowe dokumenty PDF, generuje obrazy PNG i SVG z metadanymi OCR
"""

import os
import fitz  # PyMuPDF
import subprocess
import json
import base64
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from lxml import etree as ET
from PIL import Image
import io
import time
import concurrent.futures
import logging
from datetime import datetime

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class PDFOCRProcessor:
    def __init__(self, documents_folder: str = "documents", output_folder: str = "output"):
        """
        Inicjalizuje procesor PDF z OCR

        Args:
            documents_folder: Folder z dokumentami PDF
            output_folder: Folder wyjściowy dla wygenerowanych plików
        """
        self.documents_folder = Path(documents_folder)
        self.output_folder = Path(output_folder)
        self.output_folder.mkdir(exist_ok=True)

        # Konfiguracja
        self.max_workers = 4  # Dla przetwarzania równoległego
        self.timeout = 300  # 5 minut timeout dla OCR
        self.max_image_size = (2048, 2048)  # Maksymalny rozmiar obrazu
        
        # Nowe opcje konfiguracyjne
        self.translate_to_polish = True  # Domyślnie tłumacz na polski
        self.display_mode = 'scroll'  # 'scroll' lub 'grid'
        self.show_ocr_highlights = True  # Czy pokazywać podświetlenia OCR

        # Sprawdzenie czy Ollama jest dostępne
        self.available_models = self.check_ollama_and_models()
        
        # Słownik tłumaczeń
        self.translations = {}
        self._load_translations()
        
    def _load_translations(self):
        """Wczytuje słownik tłumaczeń"""
        # Można rozszerzyć o wczytywanie z pliku
        self.translations = {
            'page': 'Strona',
            'of': 'z',
            'show_original': 'Pokaż oryginał',
            'show_translation': 'Pokaż tłumaczenie',
            'toggle_highlights': 'Przełącz podświetlenia OCR',
            'display_mode': 'Tryb wyświetlania',
            'mode_scroll': 'Przewijanie',
            'mode_grid': 'Siatka'
        }

    def check_ollama_and_models(self) -> List[str]:
        """Sprawdza czy Ollama jest zainstalowana i dostępna oraz listuje modele"""
        try:
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                raise Exception(f"Ollama nie odpowiada: {result.stderr}")

            # Parsuj dostępne modele
            models = []
            for line in result.stdout.split('\n')[1:]:  # Pomiń nagłówek
                if line.strip():
                    model_name = line.split()[0]
                    if model_name and ':' in model_name:
                        models.append(model_name)

            logger.info(f"✓ Ollama jest dostępna z modelami: {models}")
            return models

        except subprocess.TimeoutExpired:
            raise Exception("Ollama nie odpowiada - timeout")
        except FileNotFoundError:
            raise Exception("Ollama nie jest zainstalowana. Zainstaluj z https://ollama.ai")
        except Exception as e:
            raise Exception(f"Błąd sprawdzania Ollama: {e}")

    def validate_model(self, model: str) -> bool:
        """Sprawdza czy model jest dostępny"""
        return model in self.available_models

    def extract_text_with_ollama(self, image_path: str, model: str = "llava:7b") -> Dict[str, Any]:
        """
        Ekstraktuje tekst z obrazu używając Ollama OCR - POPRAWIONA WERSJA

        Args:
            image_path: Ścieżka do obrazu
            model: Model OCR do użycia

        Returns:
            Słownik z wyekstraktowanym tekstem i metadanymi
        """
        try:
            # Sprawdź czy model jest dostępny
            if not self.validate_model(model):
                logger.warning(f"Model {model} nie jest dostępny. Dostępne: {self.available_models}")
                if self.available_models:
                    model = self.available_models[0]
                    logger.info(f"Używam dostępnego modelu: {model}")
                else:
                    return self._empty_ocr_result("Brak dostępnych modeli")

            # Sprawdź czy plik istnieje
            if not Path(image_path).exists():
                return self._empty_ocr_result(f"Plik nie istnieje: {image_path}")

            # Przygotuj prompt dla OCR
            prompt = """Przeanalizuj ten obraz i wyekstraktuj cały widoczny tekst. 
Zwróć wynik w formacie JSON z następującymi polami:
{
    "text": "cały wyekstraktowany tekst",
    "confidence": 0.95,
    "language": "wykryty język (pl/en/de/fr itp.)",
    "blocks": [
        {
            "text": "tekst bloku", 
            "bbox": [x, y, width, height],
            "confidence": 0.95
        }
    ]
}

WAŻNE: Odpowiedz TYLKO kodem JSON, bez dodatkowych komentarzy."""

            # POPRAWKA: Używamy właściwego API Ollama dla obrazów
            cmd = [
                'ollama', 'run', model,
                f'"{prompt}"'
            ]

            # Przeczytaj obraz i przekaż jako stdin
            with open(image_path, 'rb') as img_file:
                img_data = img_file.read()

            # Wywołanie Ollama z timeout
            result = subprocess.run(
                cmd,
                input=img_data,
                capture_output=True,
                timeout=self.timeout
            )

            if result.returncode == 0:
                try:
                    # Wyczyść odpowiedź z potencjalnych artefaktów
                    response_text = result.stdout.decode('utf-8').strip()

                    # Znajdź JSON w odpowiedzi
                    json_start = response_text.find('{')
                    json_end = response_text.rfind('}') + 1

                    if json_start >= 0 and json_end > json_start:
                        json_text = response_text[json_start:json_end]
                        parsed_result = json.loads(json_text)

                        # Walidacja struktury odpowiedzi
                        return self._validate_ocr_result(parsed_result)
                    else:
                        # Fallback - zwróć surowy tekst
                        return {
                            "text": response_text,
                            "confidence": 0.7,
                            "language": "unknown",
                            "blocks": []
                        }

                except json.JSONDecodeError as e:
                    logger.warning(f"Błąd parsowania JSON: {e}")
                    # Fallback - zwróć surową odpowiedź
                    return {
                        "text": result.stdout.decode('utf-8', errors='ignore'),
                        "confidence": 0.6,
                        "language": "unknown",
                        "blocks": []
                    }
            else:
                error_msg = result.stderr.decode('utf-8', errors='ignore')
                logger.error(f"Błąd OCR: {error_msg}")
                return self._empty_ocr_result(f"Błąd Ollama: {error_msg}")

        except subprocess.TimeoutExpired:
            logger.error(f"Timeout OCR dla {image_path}")
            return self._empty_ocr_result("Timeout podczas OCR")
        except Exception as e:
            logger.error(f"Błąd podczas OCR {image_path}: {e}")
            return self._empty_ocr_result(f"Błąd: {e}")

    def _empty_ocr_result(self, error_msg: str = "") -> Dict[str, Any]:
        """Zwraca pusty wynik OCR"""
        return {
            "text": "",
            "confidence": 0.0,
            "language": "unknown",
            "blocks": [],
            "error": error_msg
        }

    def _validate_ocr_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Waliduje i normalizuje wynik OCR"""
        validated = {
            "text": str(result.get("text", "")),
            "confidence": float(result.get("confidence", 0.0)),
            "language": str(result.get("language", "unknown")),
            "blocks": []
        }

        # Waliduj bloki
        blocks = result.get("blocks", [])
        if isinstance(blocks, list):
            for block in blocks:
                if isinstance(block, dict):
                    bbox = block.get("bbox", [])
                    if isinstance(bbox, list) and len(bbox) >= 4:
                        validated_block = {
                            "text": str(block.get("text", "")),
                            "bbox": [float(x) for x in bbox[:4]],
                            "confidence": float(block.get("confidence", 0.0))
                        }
                        validated["blocks"].append(validated_block)

        return validated

    def resize_image_if_needed(self, image_path: str) -> str:
        """
        Zmniejsza obraz jeśli jest za duży (dla wydajności OCR)

        Args:
            image_path: Ścieżka do obrazu

        Returns:
            Ścieżka do obrazu (oryginalnego lub zmniejszonego)
        """
        try:
            with Image.open(image_path) as img:
                if img.size[0] > self.max_image_size[0] or img.size[1] > self.max_image_size[1]:
                    # Oblicz nowy rozmiar zachowując proporcje
                    img.thumbnail(self.max_image_size, Image.Resampling.LANCZOS)

                    # Zapisz zmniejszony obraz
                    resized_path = str(Path(image_path).with_suffix('.resized.png'))
                    img.save(resized_path, 'PNG', optimize=True)

                    logger.info(f"Zmniejszono obraz: {image_path} -> {resized_path}")
                    return resized_path

            return image_path

        except Exception as e:
            logger.warning(f"Nie można zmniejszyć obrazu {image_path}: {e}")
            return image_path

    def pdf_to_images(self, pdf_path: str, dpi: int = 200) -> List[str]:
        """
        Konwertuje strony PDF na obrazy PNG - POPRAWIONA WERSJA

        Args:
            pdf_path: Ścieżka do pliku PDF
            dpi: Rozdzielczość obrazów (domyślnie 200 DPI dla lepszej wydajności)

        Returns:
            Lista ścieżek do wygenerowanych obrazów PNG
        """
        pdf_name = Path(pdf_path).stem
        output_dir = self.output_folder / pdf_name
        output_dir.mkdir(exist_ok=True)

        image_paths = []

        try:
            # Otwórz dokument PDF
            doc = fitz.open(pdf_path)
            total_pages = len(doc)

            logger.info(f"Konwersja PDF: {pdf_path} ({total_pages} stron)")

            for page_num in range(total_pages):
                try:
                    page = doc.load_page(page_num)

                    # Konwertuj stronę na obraz z określonym DPI
                    mat = fitz.Matrix(dpi / 72, dpi / 72)
                    pix = page.get_pixmap(matrix=mat)

                    # Zapisz jako PNG
                    image_path = output_dir / f"page_{page_num + 1:03d}.png"
                    pix.save(str(image_path))

                    # Zmniejsz obraz jeśli potrzeba
                    final_image_path = self.resize_image_if_needed(str(image_path))
                    image_paths.append(final_image_path)

                    logger.info(f"✓ Strona {page_num + 1}/{total_pages}: {image_path}")

                except Exception as e:
                    logger.error(f"Błąd konwersji strony {page_num + 1}: {e}")
                    continue

            doc.close()
            return image_paths

        except Exception as e:
            logger.error(f"Błąd podczas konwersji PDF {pdf_path}: {e}")
            return []

    def process_ocr_parallel(self, image_paths: List[str], model: str) -> List[Dict[str, Any]]:
        """
        Przetwarzanie OCR równoległe dla lepszej wydajności

        Args:
            image_paths: Lista ścieżek do obrazów
            model: Model OCR do użycia

        Returns:
            Lista wyników OCR
        """
        logger.info(f"Rozpoczynam równoległe OCR dla {len(image_paths)} obrazów")

        ocr_results = []

        # Przetwarzanie równoległe z ograniczoną liczbą workerów
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Utwórz zadania
            future_to_path = {
                executor.submit(self.extract_text_with_ollama, path, model): path
                for path in image_paths
            }

            # Zbierz wyniki
            for future in concurrent.futures.as_completed(future_to_path):
                image_path = future_to_path[future]
                try:
                    result = future.result()
                    ocr_results.append(result)
                    logger.info(f"✓ OCR zakończone: {Path(image_path).name}")
                except Exception as e:
                    logger.error(f"Błąd OCR dla {image_path}: {e}")
                    ocr_results.append(self._empty_ocr_result(f"Błąd: {e}"))

        return ocr_results

    def _translate_text(self, text: str, source_lang: str = 'auto', target_lang: str = 'pl') -> str:
        """Tłumaczy tekst na język polski"""
        if not text or not self.translate_to_polish or target_lang == source_lang:
            return text
            
        try:
            # Proste tłumaczenie - w rzeczywistości można by użyć API tłumacza
            # To jest uproszczony przykład i powinien zostać zastąpiony prawdziwym tłumaczeniem
            if source_lang.lower() != 'pl':
                # Symulacja tłumaczenia - w rzeczywistości należy użyć API tłumacza
                # np. Google Translate API, DeepL API itp.
                return f"[PL] {text}"  # Tymczasowe rozwiązanie
            return text
        except Exception as e:
            logger.error(f"Błąd tłumaczenia: {e}")
            return text
            
    def create_optimized_svg(self, pdf_path: str, image_paths: List[str],
                             ocr_results: List[Dict[str, Any]]) -> str:
        """
        Tworzy zoptymalizowany plik SVG z metadanymi OCR i tłumaczeniem

        Args:
            pdf_path: Ścieżka do oryginalnego PDF
            image_paths: Lista ścieżek do obrazów PNG
            ocr_results: Lista wyników OCR dla każdej strony

        Returns:
            Ścieżka do wygenerowanego pliku SVG
        """
        pdf_name = Path(pdf_path).stem
        svg_path = self.output_folder / f"{pdf_name}_complete.svg"

        try:
            # Znajdź maksymalne wymiary dla normalizacji
            max_width, max_height = 0, 0
            page_dimensions = []

            for image_path in image_paths:
                try:
                    with Image.open(image_path) as img:
                        w, h = img.size
                        page_dimensions.append((w, h))
                        max_width = max(max_width, w)
                        max_height = max(max_height, h)
                except Exception as e:
                    logger.warning(f"Nie można odczytać wymiarów {image_path}: {e}")
                    page_dimensions.append((800, 600))  # Domyślne wymiary

            # Oblicz całkowitą wysokość SVG (dla trybu przewijania)
            total_height = max_height * len(image_paths)
            
            # Oblicz wymiary dla trybu siatki (2 kolumny)
            num_columns = 2
            num_rows = (len(image_paths) + 1) // num_columns
            grid_width = (max_width + 20) * num_columns
            grid_height = (max_height + 20) * num_rows

            # Tworzenie głównego elementu SVG
            svg_root = ET.Element("svg", 
                nsmap={None: "http://www.w3.org/2000/svg", "xlink": "http://www.w3.org/1999/xlink"},
                attrib={
                    "width": str(max_width),
                    "height": str(total_height),
                    "viewBox": f"0 0 {max_width} {total_height}",
                    "data-display-mode": self.display_mode,
                    "data-translate-to-polish": str(self.translate_to_polish).lower()
                }
            )

            # Dodaj metadane dokumentu i kontrolki interfejsu
            self._add_document_metadata(svg_root, pdf_path, len(image_paths))
            
            # Dodaj grupę dla stron
            pages_group = ET.SubElement(svg_root, "g", attrib={"id": "pages"})

            # Dodaj strony
            for i, (image_path, ocr_result) in enumerate(zip(image_paths, ocr_results)):
                page_group = ET.SubElement(pages_group, "g", attrib={"id": f"page_{i+1}"})
                
                # Dodaj obraz jako tło
                image_elem = ET.SubElement(page_group, "image", 
                    attrib={
                        "xlink:href": str(image_path),
                        "width": str(page_dimensions[i][0]),
                        "height": str(page_dimensions[i][1]),
                        "x": "0",
                        "y": str(i * max_height)
                    }
                )
                
                # Dodaj metadane OCR
                self._add_ocr_metadata_to_page(page_group, ocr_result, 1.0, 0.0)

            # Zapisz SVG
            self._save_svg_with_formatting(svg_root, svg_path)

            return svg_path

        except Exception as e:
            logger.error(f"Błąd podczas tworzenia SVG {pdf_path}: {e}")
            return ""

    def _add_ocr_metadata_to_page(self, page_group: ET.Element, ocr_result: Dict[str, Any],
                                 scale: float, offset_x: float):
        """
        Dodaje metadane OCR do strony wraz z warstwą tekstu do zaznaczania
        
        Args:
            page_group: Element SVG, do którego dodajemy metadane
            ocr_result: Wynik OCR z danymi tekstowymi i bounding boxami
            scale: Skala do przeskalowania współrzędnych
            offset_x: Przesunięcie X dla wycentrowania
        """
        # Pobierz grupę nadrzędną (scroll lub grid)
        parent = page_group.getparent()
        is_grid = 'grid' in parent.get('class', '') if parent is not None else False
        
        # Metadane strony
        page_metadata = ET.SubElement(page_group, "metadata")
        ocr_info = ET.SubElement(page_metadata, "ocr-data")
        ocr_info.set("confidence", str(ocr_result.get("confidence", 0.0)))
        ocr_info.set("language", str(ocr_result.get("language", "unknown")))
        ocr_info.set("text-length", str(len(ocr_result.get("text", ""))))
        
        # Dodaj oryginalny język jako atrybut
        if 'language' in ocr_result and ocr_result['language'] != 'unknown':
            page_group.set("data-original-language", str(ocr_result['language']))
            
        # Dodaj styl CSS dla warstwy tekstu
        style = ET.SubElement(page_group, "style")
        style.text = """
        .ocr-text-overlay {
            pointer-events: all;
            user-select: text;
            -webkit-user-select: text;
            -moz-user-select: text;
            -ms-user-select: text;
            font-family: Arial, sans-serif;
            fill: #000;
            white-space: pre;
        }
        .ocr-text-bg {
            fill: rgba(255, 255, 255, 0.7);
            pointer-events: none;
        }
        .ocr-text-block {
            cursor: text;
        }
        .ocr-text-block:hover .ocr-text-bg {
            fill: rgba(200, 230, 255, 0.8);
        }
        """

        # Główny tekst (niewidoczny, dla wyszukiwania)
        if ocr_result.get("text"):
            text_elem = ET.SubElement(page_group, "text", 
                x=str(offset_x),
                y="40",  # Niżej, aby uniknąć nakładania się z numerem strony
                opacity="0",
                font_size="1",
                class_="ocr-text searchable"
            )
            text_elem.text = str(ocr_result["text"][:1000])  # Ogranicz długość

        # Bloki tekstu z pozycjami
        for i, block in enumerate(ocr_result.get("blocks", [])):
            if "bbox" in block and len(block["bbox"]) >= 4:
                x, y, w, h = block["bbox"][:4]
                

                # Przeskaluj współrzędne
                scaled_x = x * scale + offset_x
                scaled_y = y * scale + (40 if not is_grid else 0)  # Uwzględnij offset dla numeru strony w trybie scroll
                scaled_w = w * scale
                scaled_h = h * scale
                
                # Unikalne ID bloku
                block_id = f"block_{i}"
                
                # Grupa dla bloku
                block_group = ET.SubElement(page_group, "g", {
                    "id": f"{page_group.get('id')}_{block_id}",
                    "class": "text-block ocr-text-block",  # Dodano klasę ocr-text-block
                    "data-confidence": str(block.get("confidence", 0.0)),
                    "data-language": str(block.get("language", "unknown")),
                    "data-original-text": block.get("text", "")[:500]  # Zachowaj oryginalny tekst
                })
                
                # Dodaj widoczny, zaznaczalny tekst
                if block.get("text"):
                    # Oblicz rozmiar czcionki na podstawie wysokości bounding boxa
                    font_size = max(8, min(24, scaled_h * 0.8))  # Ogranicz rozmiar czcionki 8-24px
                    
                    # Dodaj tło dla lepszej czytelności
                    ET.SubElement(block_group, "rect", {
                        "x": str(scaled_x - 1),
                        "y": str(scaled_y - 1),
                        "width": str(scaled_w + 2),
                        "height": str(scaled_h + 2),
                        "class": "ocr-text-bg",
                        "rx": "2",
                        "ry": "2"
                    })
                    
                    # Dodaj widoczny tekst
                    text_elem = ET.SubElement(block_group, "text", {
                        "x": str(scaled_x + 2),  # Mały margines
                        "y": str(scaled_y + font_size),  # Ustawienie baseline
                        "font-size": f"{font_size}px",
                        "class": "ocr-text-overlay"
                    })
                    text_elem.text = block["text"]
                    
                    # Dodaj tytuł z pełnym tekstem (wyświetlany po najechaniu)
                    ET.SubElement(block_group, "title").text = block["text"]
                    
                    # Dodaj niewidoczny tekst dla wyszukiwania
                    hidden_text = ET.SubElement(block_group, "text", {
                        "x": "0",
                        "y": "0",
                        "opacity": "0",
                        "font-size": "1",
                        "class": "searchable"
                    })
                    hidden_text.text = block["text"]

                # Zachowaj oryginalny tekst jako atrybut
                block_group.set("data-text", block.get("text", "")[:500])
                
                # Jeśli język to nie polski, dodaj tłumaczenie
                block_lang = block.get("language", "unknown").lower()
                if self.translate_to_polish and block_lang not in ['pl', 'polish', 'polski'] and block.get("text"):
                    translated_text = self._translate_text(
                        block["text"], 
                        source_lang=block_lang,
                        target_lang='pl'
                    )
                    if translated_text and translated_text != block["text"]:
                        # Dodaj przetłumaczony tekst
                        ET.SubElement(block_group, "text", {
                            "x": str(scaled_x),
                            "y": str(scaled_y + scaled_h + 15),  # 15px poniżej oryginału
                            "class": "translation hidden",
                            "font-size": "10",
                            "fill": "#2196F3"
                        }).text = translated_text[:200]  # Ogranicz długość

    def _save_svg_with_formatting(self, svg_root: ET.Element, svg_path: Path):
        """Zapisuje SVG z właściwym formatowaniem"""
        # Dodaj komentarz informacyjny
        comment = ET.Comment(f" Generated by PDF-OCR-Processor on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ")
        svg_root.addprevious(comment)

        # Upewnij się, że mamy prawidłowe przestrzenie nazw
        svg_root.attrib['xmlns'] = "http://www.w3.org/2000/svg"
        svg_root.attrib['xmlns:xlink'] = "http://www.w3.org/1999/xlink"

        # Zapisz z odpowiednim encoding
        with open(svg_path, 'wb') as f:
            f.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
            # Użyj tostring z opcją with_tail=False, aby uniknąć niechcianych końcówek
            f.write(ET.tostring(svg_root, pretty_print=True, encoding='utf-8', 
                              xml_declaration=False, with_tail=False))

    def process_pdf(self, pdf_path: str, ocr_model: str = "llava:7b",
                    parallel_ocr: bool = True) -> Dict[str, Any]:
        """
        Przetwarza pojedynczy plik PDF - POPRAWIONA WERSJA

        Args:
            pdf_path: Ścieżka do pliku PDF
            ocr_model: Model OCR do użycia
            parallel_ocr: Czy używać przetwarzania równoległego

        Returns:
            Słownik z wynikami przetwarzania
        """
        start_time = time.time()
        logger.info(f"🔄 Przetwarzanie: {pdf_path}")

        try:
            # Sprawdź czy plik istnieje
            if not Path(pdf_path).exists():
                return {"error": f"Plik nie istnieje: {pdf_path}"}

            # Sprawdź rozmiar pliku
            file_size = Path(pdf_path).stat().st_size
            if file_size > 100 * 1024 * 1024:  # 100MB
                logger.warning(f"Duży plik PDF ({file_size / 1024 / 1024:.1f}MB): {pdf_path}")

            # Konwertuj PDF na obrazy
            image_paths = self.pdf_to_images(pdf_path)

            if not image_paths:
                return {"error": "Nie udało się skonwertować PDF na obrazy"}

            logger.info(f"✓ Wygenerowano {len(image_paths)} obrazów PNG")

            # Wykonaj OCR
            if parallel_ocr and len(image_paths) > 1:
                ocr_results = self.process_ocr_parallel(image_paths, ocr_model)
            else:
                ocr_results = []
                for i, image_path in enumerate(image_paths):
                    logger.info(f"🔍 OCR strona {i + 1}/{len(image_paths)}")
                    result = self.extract_text_with_ollama(image_path, ocr_model)
                    ocr_results.append(result)

            # Utwórz SVG tylko jeśli jest więcej niż jedna strona
            svg_path = None
            if len(image_paths) > 1:
                svg_path = self.create_optimized_svg(pdf_path, image_paths, ocr_results)

            # Oblicz statystyki
            total_text_length = sum(len(result.get("text", "")) for result in ocr_results)
            avg_confidence = sum(result.get("confidence", 0.0) for result in ocr_results) / len(
                ocr_results) if ocr_results else 0.0

            processing_time = time.time() - start_time

            result = {
                "pdf_path": pdf_path,
                "page_count": len(image_paths),
                "image_paths": image_paths,
                "svg_path": svg_path,
                "ocr_results": ocr_results,
                "total_text_length": total_text_length,
                "average_confidence": avg_confidence,
                "processing_time": processing_time,
                "timestamp": datetime.now().isoformat()
            }

            logger.info(f"✅ Zakończono przetwarzanie {pdf_path} w {processing_time:.1f}s")
            return result

        except Exception as e:
            logger.error(f"Błąd podczas przetwarzania {pdf_path}: {e}")
            return {
                "pdf_path": pdf_path,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def process_all_pdfs(self, ocr_model: str = "llava:7b",
                         parallel_ocr: bool = True) -> List[Dict[str, Any]]:
        """
        Przetwarza wszystkie pliki PDF w folderze documents - POPRAWIONA WERSJA

        Args:
            ocr_model: Model OCR do użycia
            parallel_ocr: Czy używać przetwarzania równoległego dla OCR

        Returns:
            Lista wyników przetwarzania
        """
        if not self.documents_folder.exists():
            logger.error(f"Folder {self.documents_folder} nie istnieje")
            return []

        # Znajdź wszystkie pliki PDF
        pdf_files = sorted(list(self.documents_folder.glob("*.pdf")))

        if not pdf_files:
            logger.warning(f"Brak plików PDF w folderze {self.documents_folder}")
            return []

        logger.info(f"📁 Znaleziono {len(pdf_files)} plików PDF")

        # Sprawdź model
        if not self.validate_model(ocr_model):
            if self.available_models:
                ocr_model = self.available_models[0]
                logger.info(f"Używam dostępnego modelu: {ocr_model}")
            else:
                logger.error("Brak dostępnych modeli OCR")
                return []

        results = []
        for i, pdf_file in enumerate(pdf_files):
            try:
                logger.info(f"\n📄 Plik {i + 1}/{len(pdf_files)}: {pdf_file.name}")
                result = self.process_pdf(str(pdf_file), ocr_model, parallel_ocr)
                results.append(result)

                # Krótka pauza między plikami
                if i < len(pdf_files) - 1:
                    time.sleep(1)

            except KeyboardInterrupt:
                logger.info("Przerwano przez użytkownika")
                break
            except Exception as e:
                logger.error(f"Błąd podczas przetwarzania {pdf_file}: {e}")
                results.append({
                    "pdf_path": str(pdf_file),
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })

        return results

    def generate_detailed_report(self, results: List[Dict[str, Any]]) -> str:
        """
        Generuje szczegółowy raport z wyników przetwarzania - POPRAWIONA WERSJA

        Args:
            results: Lista wyników przetwarzania

        Returns:
            Ścieżka do pliku z raportem
        """
        report_path = self.output_folder / "processing_report.json"

        # Przygotuj szczegółowe podsumowanie
        successful = [r for r in results if "error" not in r]
        failed = [r for r in results if "error" in r]

        total_pages = sum(r.get("page_count", 0) for r in successful)
        total_processing_time = sum(r.get("processing_time", 0) for r in successful)
        avg_confidence = sum(r.get("average_confidence", 0) for r in successful) / len(successful) if successful else 0

        summary = {
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "processor_version": "2.0",
                "total_files_processed": len(results)
            },
            "statistics": {
                "successful_files": len(successful),
                "failed_files": len(failed),
                "total_pages": total_pages,
                "svg_files_created": len([r for r in successful if r.get("svg_path")]),
                "total_processing_time_seconds": total_processing_time,
                "average_confidence": avg_confidence,
                "average_time_per_page": total_processing_time / total_pages if total_pages > 0 else 0
            },
            "model_info": {
                "ocr_models_available": self.available_models,
                "processor_config": {
                    "max_workers": self.max_workers,
                    "timeout": self.timeout,
                    "max_image_size": self.max_image_size
                }
            },
            "file_results": results,
            "errors": [
                {
                    "file": r["pdf_path"],
                    "error": r["error"],
                    "timestamp": r.get("timestamp", "")
                } for r in failed
            ]
        }

        # Zapisz raport z ładnym formatowaniem
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        logger.info(f"📊 Szczegółowy raport zapisany: {report_path}")
        return str(report_path)

    def cleanup_temp_files(self):
        """Usuwa tymczasowe pliki po przetwarzaniu"""
        try:
            # Znajdź i usuń pliki .resized.png
            for resized_file in self.output_folder.rglob("*.resized.png"):
                resized_file.unlink()
                logger.debug(f"Usunięto tymczasowy plik: {resized_file}")
        except Exception as e:
            logger.warning(f"Błąd podczas usuwania plików tymczasowych: {e}")


def validate_requirements():
    """Sprawdza czy wszystkie wymagania są spełnione"""
    print("🔍 Sprawdzanie wymagań systemowych...")

    missing_requirements = []

    # Sprawdź PyMuPDF
    try:
        import fitz
        print("✅ PyMuPDF: OK")
    except ImportError:
        missing_requirements.append("PyMuPDF (pip install PyMuPDF)")

    # Sprawdź Pillow
    try:
        from PIL import Image
        print("✅ Pillow: OK")
    except ImportError:
        missing_requirements.append("Pillow (pip install Pillow)")

    # Sprawdź Ollama
    try:
        result = subprocess.run(['ollama', '--version'], capture_output=True, timeout=5)
        if result.returncode == 0:
            print("✅ Ollama: OK")
        else:
            missing_requirements.append("Ollama (https://ollama.ai)")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        missing_requirements.append("Ollama (https://ollama.ai)")

    if missing_requirements:
        print("\n❌ Brakujące wymagania:")
        for req in missing_requirements:
            print(f"  - {req}")
        return False

    print("\n✅ Wszystkie wymagania spełnione!")
    return True


def interactive_model_selection(processor: PDFOCRProcessor) -> str:
    """Interaktywny wybór modelu OCR"""
    available_models = processor.available_models

    if not available_models:
        print("❌ Brak dostępnych modeli OCR")
        print("💡 Pobierz modele komendami:")
        print("   ollama pull llava:7b")
        print("   ollama pull llama3.2-vision")
        return ""

    print(f"\n🤖 Dostępne modele OCR ({len(available_models)}):")
    for i, model in enumerate(available_models, 1):
        # Dodaj opisy modeli
        description = ""
        if "llava" in model.lower():
            description = " (szybki, uniwersalny)"
        elif "llama3.2-vision" in model.lower():
            description = " (wysoka dokładność)"
        elif "moondream" in model.lower():
            description = " (kompaktowy)"

        print(f"  {i}. {model}{description}")

    while True:
        try:
            choice = input(f"\nWybierz model (1-{len(available_models)}, domyślnie 1): ").strip()

            if not choice:
                return available_models[0]

            index = int(choice) - 1
            if 0 <= index < len(available_models):
                return available_models[index]
            else:
                print(f"❌ Wybierz liczbę od 1 do {len(available_models)}")

        except ValueError:
            print("❌ Wprowadź poprawną liczbę")
        except KeyboardInterrupt:
            print("\n🛑 Anulowano")
            return ""


def main(config=None):
    """
    Główna funkcja programu - POPRAWIONA WERSJA
    
    Args:
        config (dict, optional): Konfiguracja programu. Może zawierać:
            - input_path: Ścieżka do pliku PDF lub folderu z plikami PDF
            - output_folder: Folder wyjściowy
            - model: Nazwa modelu OCR do użycia
            - workers: Liczba wątków roboczych
            - non_interactive: Czy działać w trybie nieinterakcyjnym (bez pytań do użytkownika)
    """
    if config is None:
        config = {}
    
    # Ustaw tryb nieinteraktywny jeśli podano jakiekolwiek argumenty wiersza poleceń
    if not config.get('non_interactive') and (config.get('input_path') or config.get('model') or config.get('workers')):
        config['non_interactive'] = True
        
    print("🚀 PDF Multi-Page OCR Processor v2.0")
    print("=" * 50)

    # Sprawdź wymagania
    if not validate_requirements():
        print("\n❌ Nie można kontynuować - brakujące wymagania")
        return 1

    try:
        # Inicjalizuj procesor z customowymi ścieżkami jeśli podane
        documents_folder = Path(config.get('input_path', 'documents'))
        output_folder = Path(config.get('output_folder', 'output'))
        
        print(f"\n⚙️ Inicjalizacja processora...")
        print(f"  - Folder wejściowy: {documents_folder}")
        print(f"  - Folder wyjściowy: {output_folder}")
        
        processor = PDFOCRProcessor(
            documents_folder=str(documents_folder.parent if documents_folder.is_file() else documents_folder),
            output_folder=str(output_folder)
        )

        # Ustawienie liczby workerów jeśli podana
        if 'workers' in config:
            processor.max_workers = int(config['workers'])

        # Sprawdź czy folder wejściowy istnieje
        if not documents_folder.exists():
            if config.get('non_interactive'):
                print(f"\n❌ Błąd: Folder wejściowy nie istnieje: {documents_folder}")
                return 1
            print(f"\n📁 Tworzenie folderu: {documents_folder}")
            documents_folder.mkdir(parents=True)
            print(f"💡 Umieść pliki PDF w folderze: {documents_folder}")
            return 0

        # Sprawdź czy są pliki do przetworzenia
        if documents_folder.is_file():
            # Jeśli podano bezpośredni plik PDF
            pdf_files = [documents_folder]
            # Ustaw katalog nadrzędny jako folder z dokumentami
            processor.documents_folder = documents_folder.parent
        else:
            # W przeciwnym razie szukaj plików PDF w folderze
            pdf_files = list(documents_folder.glob("*.pdf"))
            
        if not pdf_files:
            print(f"\n📭 Brak plików PDF w folderze: {documents_folder}")
            if not config.get('non_interactive'):
                print("💡 Umieść pliki PDF w tym folderze i uruchom ponownie")
            return 0

        print(f"\n📄 Znalezione pliki PDF ({len(pdf_files)}):")
        for pdf_file in pdf_files:
            size_mb = pdf_file.stat().st_size / (1024 * 1024)
            print(f"  - {pdf_file.name} ({size_mb:.1f} MB)")

        # Wybór modelu OCR
        selected_model = config.get('model')
        if not selected_model:
            if config.get('non_interactive'):
                # W trybie nieinterakcyjnym używamy domyślnego modelu
                selected_model = "llava:7b"
                print(f"\n🔧 Używany model (domyślny): {selected_model}")
            else:
                selected_model = interactive_model_selection(processor)
                if not selected_model:
                    return 1
        else:
            # Sprawdź czy wybrany model jest dostępny
            available_models = processor.check_ollama_and_models()
            if selected_model not in available_models:
                print(f"\n❌ Błąd: Model {selected_model} nie jest dostępny")
                print("Dostępne modele:")
                for model in available_models:
                    print(f"  - {model}")
                return 1

        print(f"\n🔧 Używany model: {selected_model}")

        # Konfiguracja przetwarzania
        print("\n⚙️ Konfiguracja:")
        use_parallel = True  # Domyślnie włączone
        
        if not config.get('non_interactive'):
            parallel_choice = input("Użyć przetwarzania równoległego? (T/n): ").strip().lower()
            use_parallel = parallel_choice != 'n'

        if use_parallel and not config.get('non_interactive') and not config.get('workers'):
            workers_input = input(f"Liczba workerów (domyślnie {processor.max_workers}): ").strip()
            if workers_input.isdigit():
                processor.max_workers = int(workers_input)

        print(f"  - Przetwarzanie równoległe: {'✅' if use_parallel else '❌'}")
        print(f"  - Liczba workerów: {processor.max_workers}")
        print(f"  - Timeout OCR: {processor.timeout}s")

        # Rozpocznij przetwarzanie
        print(f"\n🚀 Rozpoczynam przetwarzanie {len(pdf_files)} plików...")
        print("=" * 50)

        start_time = time.time()
        results = processor.process_all_pdfs(selected_model, use_parallel)
        total_time = time.time() - start_time

        # Wygeneruj raport
        if results:
            report_path = processor.generate_detailed_report(results)

            # Sprzątanie
            processor.cleanup_temp_files()

            # Wyświetl podsumowanie
            print("\n" + "=" * 50)
            print("📋 PODSUMOWANIE PRZETWARZANIA")
            print("=" * 50)

            successful = [r for r in results if "error" not in r]
            failed = [r for r in results if "error" in r]
            total_pages = sum(r.get("page_count", 0) for r in successful)

            print(f"⏱️ Całkowity czas: {total_time:.1f}s")
            print(f"✅ Pomyślnie przetworzono: {len(successful)} plików")
            print(f"❌ Błędy: {len(failed)} plików")
            print(f"📄 Łączna liczba stron: {total_pages}")
            print(f"🖼️ Pliki SVG utworzone: {len([r for r in successful if r.get('svg_path')])}")

            if total_pages > 0:
                print(f"⚡ Średni czas na stronę: {total_time / total_pages:.2f}s")

            if successful:
                avg_confidence = sum(r.get("average_confidence", 0) for r in successful) / len(successful)
                print(f"🎯 Średnia pewność OCR: {avg_confidence:.1%}")

            if failed:
                print(f"\n❌ Pliki z błędami:")
                for result in failed:
                    print(f"  - {Path(result['pdf_path']).name}: {result['error']}")

            print(f"\n📊 Szczegółowy raport: {report_path}")
            print(f"📁 Pliki wyjściowe: {processor.output_folder}")

            # Pokaż przykłady użycia wyników
            print(f"\n💡 Przykłady użycia wyników:")
            print(f"  - Otwórz SVG w przeglądarce: file://{processor.output_folder.absolute()}")
            print(f"  - Importuj PNG: {processor.output_folder}/<nazwa_pdf>/")
            print(f"  - Analiza JSON: {report_path}")

        else:
            print("❌ Nie przetworzono żadnych plików")
            return 1

        return 0

    except KeyboardInterrupt:
        print("\n\n🛑 Przerwano przez użytkownika")
        return 130
    except Exception as e:
        logger.error(f"Nieoczekiwany błąd: {e}")
        print(f"\n❌ Krytyczny błąd: {e}")
        return 1


if __name__ == "__main__":
    import sys

    exit_code = main()
    sys.exit(exit_code)
