#!/bin/bash

# PDF OCR Processor - Skrypt instalacyjny v2.0
# Automatycznie instaluje wszystkie zależności i konfiguruje środowisko

set -e  # Zatrzymaj na pierwszym błędzie

# Kolory dla lepszej czytelności
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Funkcje pomocnicze
print_header() {
    echo -e "${PURPLE}============================================${NC}"
    echo -e "${PURPLE}🚀 PDF OCR Processor - Instalator v2.0${NC}"
    echo -e "${PURPLE}============================================${NC}"
}

print_step() {
    echo -e "\n${CYAN}📋 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Sprawdź czy komenda istnieje
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Wykryj system operacyjny
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command_exists apt-get; then
            OS="ubuntu"
        elif command_exists yum; then
            OS="centos"
        elif command_exists pacman; then
            OS="arch"
        else
            OS="linux"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        OS="windows"
    else
        OS="unknown"
    fi
}

# Sprawdź wymagania systemowe
check_requirements() {
    print_step "Sprawdzanie wymagań systemowych"
    
    # Sprawdź Python
    if command_exists python3; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
        
        if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 8 ]; then
            print_success "Python $PYTHON_VERSION ✓"
            PYTHON_CMD="python3"
        else
            print_error "Python 3.8+ wymagany, znaleziono $PYTHON_VERSION"
            exit 1
        fi
    elif command_exists python; then
        PYTHON_VERSION=$(python --version 2>&1 | cut -d' ' -f2)
        if [[ $PYTHON_VERSION == 3.* ]]; then
            print_success "Python $PYTHON_VERSION ✓"
            PYTHON_CMD="python"
        else
            print_error "Python 3.8+ wymagany"
            exit 1
        fi
    else
        print_error "Python nie jest zainstalowany"
        print_info "Zainstaluj Python 3.8+ i uruchom ponownie"
        exit 1
    fi
    
    # Sprawdź pip
    if command_exists pip3; then
        print_success "pip3 ✓"
        PIP_CMD="pip3"
    elif command_exists pip; then
        print_success "pip ✓"
        PIP_CMD="pip"
    else
        print_error "pip nie jest zainstalowany"
        exit 1
    fi
    
    # Sprawdź git
    if command_exists git; then
        print_success "git ✓"
    else
        print_warning "git nie jest zainstalowany - instalacja z lokalnych plików"
    fi
    
    # Sprawdź curl
    if command_exists curl; then
        print_success "curl ✓"
    else
        print_warning "curl nie jest zainstalowany - może być potrzebny dla Ollama"
    fi
}

# Zainstaluj zależności systemowe
install_system_dependencies() {
    print_step "Instalowanie zależności systemowych"
    
    case $OS in
        "ubuntu")
            print_info "Aktualizacja pakietów Ubuntu/Debian..."
            sudo apt-get update
            sudo apt-get install -y python3-venv python3-pip curl git
            ;;
        "centos")
            print_info "Instalacja pakietów CentOS/RHEL..."
            sudo yum install -y python3 python3-pip curl git
            ;;
        "arch")
            print_info "Instalacja pakietów Arch Linux..."
            sudo pacman -S --noconfirm python python-pip curl git
            ;;
        "macos")
            if command_exists brew; then
                print_info "Instalacja przez Homebrew..."
                brew install python git curl
            else
                print_warning "Homebrew nie jest zainstalowany"
                print_info "Zainstaluj Homebrew: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
            fi
            ;;
        "windows")
            print_info "Windows wykryty - używaj WSL2 dla najlepszej kompatybilności"
            ;;
        *)
            print_warning "Nieznany system operacyjny - kontynuuj ręcznie"
            ;;
    esac
}

# Stwórz środowisko wirtualne
create_virtual_environment() {
    print_step "Tworzenie środowiska wirtualnego"
    
    if [ -d "venv" ]; then
        print_warning "Środowisko wirtualne już istnieje"
        read -p "Czy chcesz je usunąć i utworzyć nowe? (t/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[TtYy]$ ]]; then
            rm -rf venv
        else
            print_info "Używam istniejącego środowiska"
            return
        fi
    fi
    
    $PYTHON_CMD -m venv venv
    print_success "Środowisko wirtualne utworzone"
    
    # Aktywuj środowisko
    source venv/bin/activate
    print_success "Środowisko wirtualne aktywowane"
    
    # Zaktualizuj pip
    pip install --upgrade pip
}

# Zainstaluj pakiety Python
install_python_dependencies() {
    print_step "Instalowanie pakietów Python"
    
    # Stwórz requirements.txt jeśli nie istnieje
    if [ ! -f "requirements.txt" ]; then
        cat > requirements.txt << EOF
# PDF OCR Processor Dependencies
PyMuPDF>=1.23.0
Pillow>=9.0.0
requests>=2.28.0
pyyaml>=6.0
tqdm>=4.64.0

# Development dependencies (optional)
pytest>=7.0.0
black>=22.0.0
flake8>=5.0.0
mypy>=1.0.0
EOF
        print_info "Utworzono requirements.txt"
    fi
    
    # Zainstaluj pakiety
    pip install -r requirements.txt
    print_success "Pakiety Python zainstalowane"
}

# Zainstaluj Ollama
install_ollama() {
    print_step "Instalowanie Ollama"
    
    if command_exists ollama; then
        print_success "Ollama już jest zainstalowana"
        return
    fi
    
    case $OS in
        "linux"|"ubuntu"|"centos"|"arch")
            print_info "Instalacja Ollama dla Linux..."
            curl -fsSL https://ollama.ai/install.sh | sh
            ;;
        "macos")
            print_info "Instalacja Ollama dla macOS..."
            if command_exists brew; then
                brew install ollama
            else
                curl -fsSL https://ollama.ai/install.sh | sh
            fi
            ;;
        "windows")
            print_info "Dla Windows pobierz Ollama z: https://ollama.ai/download"
            print_warning "Po instalacji uruchom ponownie ten skrypt"
            exit 1
            ;;
        *)
            print_warning "Automatyczna instalacja Ollama niedostępna dla $OS"
            print_info "Zainstaluj ręcznie z: https://ollama.ai"
            exit 1
            ;;
    esac
    
    # Sprawdź czy Ollama działa
    sleep 2
    if command_exists ollama; then
        print_success "Ollama zainstalowana pomyślnie"
    else
        print_error "Instalacja Ollama nie powiodła się"
        exit 1
    fi
}

# Uruchom Ollama service
start_ollama_service() {
    print_step "Uruchamianie serwisu Ollama"
    
    case $OS in
        "linux"|"ubuntu"|"centos"|"arch")
            if command_exists systemctl; then
                sudo systemctl start ollama 2>/dev/null || true
                sudo systemctl enable ollama 2>/dev/null || true
                print_success "Serwis Ollama uruchomiony"
            else
                print_info "Uruchamianie Ollama w tle..."
                nohup ollama serve > /dev/null 2>&1 &
                sleep 3
            fi
            ;;
        "macos")
            print_info "Uruchamianie Ollama..."
            nohup ollama serve > /dev/null 2>&1 &
            sleep 3
            ;;
    esac
    
    # Sprawdź czy serwis działa
    if ollama list >/dev/null 2>&1; then
        print_success "Serwis Ollama działa"
    else
        print_warning "Serwis Ollama może nie działać poprawnie"
    fi
}

# Pobierz modele OCR
download_ocr_models() {
    print_step "Pobieranie modeli OCR"
    
    # Lista modeli do pobrania
    MODELS=("llava:7b" "llama3.2-vision:11b")
    
    print_info "To może potrwać kilka minut..."
    
    for model in "${MODELS[@]}"; do
        print_info "Pobieranie $model..."
        if ollama pull "$model"; then
            print_success "$model pobrano"
        else
            print_warning "Nie udało się pobrać $model"
        fi
    done
    
    # Pokaż dostępne modele
    print_info "Dostępne modele:"
    ollama list
}

# Stwórz strukturę folderów
create_project_structure() {
    print_step "Tworzenie struktury projektu"
    
    mkdir -p documents
    mkdir -p output
    mkdir -p logs
    mkdir -p config
    
    # Stwórz przykładową konfigurację
    cat > config/config.yaml << EOF
# PDF OCR Processor Configuration
processing:
  max_workers: 4
  timeout_seconds: 300
  max_image_size: [2048, 2048]
  default_dpi: 200
  
ollama:
  host: "localhost:11434"
  preferred_models:
    - "llama3.2-vision:11b"
    - "llava:7b"
  
output:
  create_svg: true
  embed_images: true
  include_debug_rectangles: false
  cleanup_temp_files: true

logging:
  level: "INFO"
  log_file: "logs/pdf_ocr.log"
EOF
    
    # Stwórz .gitignore
    cat > .gitignore << EOF
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environment
venv/
env/
ENV/

# Output files
output/
logs/
*.log

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Ollama models (if stored locally)
models/
EOF
    
    print_success "Struktura projektu utworzona"
}

# Pobierz pliki projektu
download_project_files() {
    print_step "Pobieranie plików projektu"
    
    # Jeśli nie mamy git, utwórz przykładowe pliki
    if [ ! -f "pdf_processor.py" ]; then
        print_info "Tworzenie przykładowych plików..."
        
        # Główny plik (skrócona wersja)
        cat > pdf_processor.py << 'EOF'
#!/usr/bin/env python3
"""
PDF OCR Processor - Główny plik
"""

print("🚀 PDF OCR Processor v2.0")
print("Pobierz pełną wersję z repozytorium GitHub")
print("Lub skopiuj kod z dokumentacji")

if __name__ == "__main__":
    print("Uruchom: python pdf_processor.py")
EOF
        
        chmod +x pdf_processor.py
        print_info "Utworzono przykładowy plik pdf_processor.py"
        print_warning "Skopiuj pełną implementację z dokumentacji"
    fi
}

# Weryfikuj instalację
verify_installation() {
    print_step "Weryfikacja instalacji"
    
    # Sprawdź Python packages
    python -c "import fitz, PIL, yaml" 2>/dev/null && print_success "Pakiety Python ✓" || print_error "Błąd pakietów Python"
    
    # Sprawdź Ollama
    if ollama list >/dev/null 2>&1; then
        print_success "Ollama ✓"
        MODEL_COUNT=$(ollama list | tail -n +2 | wc -l)
        print_info "Dostępne modele: $MODEL_COUNT"
    else
        print_error "Ollama nie działa"
    fi
    
    # Sprawdź strukturę folderów
    [ -d "documents" ] && print_success "Folder documents ✓" || print_error "Brak folderu documents"
    [ -d "output" ] && print_success "Folder output ✓" || print_error "Brak folderu output"
    [ -f "config/config.yaml" ] && print_success "Konfiguracja ✓" || print_error "Brak konfiguracji"
    
    # Test importów
    if python -c "from pdf_processor import PDFOCRProcessor" 2>/dev/null; then
        print_success "Import głównej klasy ✓"
    else
        print_warning "Główna klasa nie jest dostępna"
    fi
}

# Pokaż instrukcje po instalacji
show_next_steps() {
    print_step "Następne kroki"
    
    echo -e "${GREEN}"
    cat << EOF

🎉 Instalacja zakończona pomyślnie!

📋 Co dalej:

1. Aktywuj środowisko wirtualne:
   source venv/bin/activate

2. Umieść pliki PDF w folderze documents/:
   cp *.pdf documents/

3. Uruchom procesor:
   python pdf_processor.py

4. Sprawdź wyniki w folderze output/

📖 Dodatkowe komendy:

• Sprawdź modele Ollama:
  ollama list

• Uruchom testy:
  python test_runner.py

• Zobacz konfigurację:
  cat config/config.yaml

• Sprawdź logi:
  tail -f logs/pdf_ocr.log

🔗 Dokumentacja:
  README.md

🐛 Problemy:
  Sprawdź sekcję Troubleshooting w README.md

EOF
    echo -e "${NC}"
}

# Menu interaktywne
interactive_menu() {
    while true; do
        echo -e "\n${BLUE}🔧 Menu instalacji:${NC}"
        echo "1. Pełna automatyczna instalacja"
        echo "2. Instalacja tylko pakietów Python"
        echo "3. Instalacja tylko Ollama"
        echo "4. Pobierz tylko modele OCR"
        echo "5. Weryfikacja instalacji"
        echo "6. Pokaż instrukcje"
        echo "0. Wyjście"
        
        read -p "Wybierz opcję (0-6): " choice
        
        case $choice in
            1)
                full_installation
                break
                ;;
            2)
                create_virtual_environment
                install_python_dependencies
                ;;
            3)
                install_ollama
                start_ollama_service
                ;;
            4)
                download_ocr_models
                ;;
            5)
                verify_installation
                ;;
            6)
                show_next_steps
                ;;
            0)
                print_info "Do widzenia!"
                exit 0
                ;;
            *)
                print_warning "Nieprawidłowa opcja"
                ;;
        esac
    done
}

# Pełna instalacja
full_installation() {
    detect_os
    print_info "Wykryto system: $OS"
    
    check_requirements
    install_system_dependencies
    create_virtual_environment
    install_python_dependencies
    create_project_structure
    download_project_files
    install_ollama
    start_ollama_service
    download_ocr_models
    verify_installation
    show_next_steps
}

# Obsługa argumentów linii komend
handle_arguments() {
    case "${1:-}" in
        "--help"|"-h")
            echo "PDF OCR Processor - Skrypt instalacyjny"
            echo ""
            echo "Użycie:"
            echo "  $0                 # Interaktywne menu"
            echo "  $0 --full          # Pełna automatyczna instalacja"
            echo "  $0 --python-only   # Tylko pakiety Python"
            echo "  $0 --ollama-only   # Tylko Ollama"
            echo "  $0 --verify        # Weryfikacja instalacji"
            echo "  $0 --help          # Ta pomoc"
            exit 0
            ;;
        "--full")
            full_installation
            exit 0
            ;;
        "--python-only")
            create_virtual_environment
            install_python_dependencies
            exit 0
            ;;
        "--ollama-only")
            install_ollama
            start_ollama_service
            download_ocr_models
            exit 0
            ;;
        "--verify")
            verify_installation
            exit 0
            ;;
        "")
            # Brak argumentów - menu interaktywne
            ;;
        *)
            print_error "Nieznany argument: $1"
            print_info "Użyj --help aby zobaczyć dostępne opcje"
            exit 1
            ;;
    esac
}

# Główna funkcja
main() {
    print_header
    
    # Sprawdź czy uruchomiono z sudo (niepotrzebne)
    if [ "$EUID" -eq 0 ]; then
        print_warning "Nie uruchamiaj tego skryptu jako root!"
        print_info "Skrypt sam poprosi o sudo gdy będzie potrzebne"
        exit 1
    fi
    
    handle_arguments "$@"
    
    # Jeśli nie było argumentów, pokaż menu
    interactive_menu
}

# Obsługa Ctrl+C
trap 'echo -e "\n\n${YELLOW}⚠️  Instalacja przerwana przez użytkownika${NC}"; exit 130' INT

# Uruchom główną funkcję z wszystkimi argumentami
main "$@"
