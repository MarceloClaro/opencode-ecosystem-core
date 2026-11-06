#!/bin/bash
#==============================================================================
# Script de instalação do ambiente OdontoIA
# Livro: Odontologia & Inteligência Artificial
# v2.0 — 2026
#
# Uso:
#   bash apendice-d-instalacao.sh            # Instalação completa
#   bash apendice-d-instalacao.sh --gpu      # Força instalação com CUDA
#   bash apendice-d-instalacao.sh --cpu      # Força instalação apenas CPU
#   bash apendice-d-instalacao.sh --verify   # Apenas verifica instalação
#   bash apendice-d-instalacao.sh --help     # Ajuda
#==============================================================================

set -euo pipefail

VERDE='\033[0;32m'
AMARELO='\033[1;33m'
VERMELHO='\033[0;31m'
AZUL='\033[0;34m'
RESET='\033[0m'

info()  { echo -e "${AZUL}[INFO]${RESET} $1"; }
ok()    { echo -e "${VERDE}[OK]${RESET} $1"; }
warn()  { echo -e "${AMARELO}[AVISO]${RESET} $1"; }
erro()  { echo -e "${VERMELHO}[ERRO]${RESET} $1"; }

#==============================================================================
# DETECÇÃO DE SISTEMA
#==============================================================================
detect_os() {
    case "$(uname -s)" in
        Linux*)     OS=linux;;
        Darwin*)    OS=macos;;
        CYGWIN*|MINGW*|MSYS*) OS=windows;;
        *)          OS=unknown;;
    esac
    info "Sistema operacional detectado: ${OS}"
}

detect_gpu() {
    if command -v nvidia-smi &> /dev/null; then
        GPU_AVAILABLE=true
        GPU_INFO=$(nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>/dev/null | head -1)
        ok "GPU NVIDIA detectada: ${GPU_INFO}"
    else
        GPU_AVAILABLE=false
        warn "Nenhuma GPU NVIDIA detectada. Usando modo CPU (lento para treinamento)."
    fi
}

#==============================================================================
# VERIFICAÇÃO DE PRÉ-REQUISITOS
#==============================================================================
check_prerequisites() {
    info "Verificando pré-requisitos..."
    local erros=0

    # Python
    if command -v python3 &> /dev/null; then
        PYTHON_VER=$(python3 --version 2>&1)
        ok "Python: ${PYTHON_VER}"
    else
        erro "Python 3 não encontrado. Instale: sudo apt install python3 python3-pip python3-venv"
        erros=$((erros+1))
    fi

    # pip
    if command -v pip3 &> /dev/null; then
        PIP_VER=$(pip3 --version 2>&1 | awk '{print $2}')
        ok "pip: ${PIP_VER}"
    else
        erro "pip não encontrado."
        erros=$((erros+1))
    fi

    # Git
    if command -v git &> /dev/null; then
        GIT_VER=$(git --version 2>&1)
        ok "Git: ${GIT_VER}"
    else
        warn "Git não encontrado. Instale: sudo apt install git"
    fi

    # make (para LaTeX)
    if command -v make &> /dev/null; then
        ok "make disponível"
    else
        warn "make não encontrado (opcional para compilar o livro)."
    fi

    return ${erros}
}

#==============================================================================
# INSTALAÇÃO DE DEPENDÊNCIAS DO SISTEMA (Linux)
#==============================================================================
install_system_deps() {
    if [ "${OS}" != "linux" ]; then
        warn "Pulando dependências de sistema (apenas Linux suportado)."
        return
    fi

    info "Instalando dependências de sistema..."
    
    # Detectar gerenciador de pacotes
    if command -v apt &> /dev/null; then
        sudo apt-get update -qq
        sudo apt-get install -y -qq --no-install-recommends \
            python3-dev \
            python3-venv \
            build-essential \
            cmake \
            libgl1-mesa-glx \
            libglib2.0-0 \
            tesseract-ocr \
            libtesseract-dev \
            libsm6 \
            libxext6 \
            libxrender-dev \
            libgomp1 \
            2>/dev/null || warn "Algumas dependências de sistema não puderam ser instaladas."
        ok "Dependências de sistema instaladas."
    elif command -v brew &> /dev/null; then
        brew install tesseract cmake pkg-config 2>/dev/null || warn "brew não disponível."
        ok "Dependências (Homebrew) instaladas."
    else
        warn "Gerenciador de pacotes não detectado. Instale manualmente: python3-dev, build-essential, cmake, tesseract-ocr"
    fi
}

#==============================================================================
# CRIAÇÃO DO AMBIENTE VIRTUAL
#==============================================================================
setup_venv() {
    if [ -d "odontoia-env" ]; then
        info "Ambiente virtual já existe. Atualizando..."
    else
        info "Criando ambiente virtual Python..."
        python3 -m venv odontoia-env
        ok "Ambiente virtual criado em ./odontoia-env/"
    fi

    source odontoia-env/bin/activate
    ok "Ambiente virtual ativado."

    # Atualizar pip
    pip install --upgrade pip -q
    ok "pip atualizado."
}

#==============================================================================
# INSTALAÇÃO DE BIBLIOTECAS PYTHON
#==============================================================================
install_python_deps() {
    info "Instalando bibliotecas Python (isso pode levar vários minutos)..."

    # Instalar dependências principais
    pip install \
        numpy==1.24.3 \
        scipy==1.10.1 \
        pandas==2.0.3 \
        matplotlib==3.7.2 \
        seaborn==0.12.2 \
        scikit-learn==1.3.0 \
        scikit-image==0.21.0 \
        opencv-python==4.8.0.74 \
        Pillow==10.0.0 \
        tqdm==4.66.1 \
        joblib==1.3.1 \
        requests==2.31.0 \
        imbalanced-learn==0.11.0 \
        -q 2>&1 | tail -5

    ok "Dependências base instaladas."

    # Deep Learning (CPU ou GPU)
    if [ "${GPU_AVAILABLE}" = true ] && [ "${FORCE_CPU:-false}" != true ]; then
        info "Instalando PyTorch com suporte CUDA..."
        pip install torch==2.0.1 torchvision==0.15.2 --index-url https://download.pytorch.org/whl/cu118 -q 2>&1 | tail -3
        
        info "Instalando TensorFlow com suporte GPU..."
        pip install tensorflow==2.12.0 -q 2>&1 | tail -3
        
        ok "Deep Learning com GPU instalado."
    else
        warn "Instalando versões CPU-only do PyTorch e TensorFlow..."
        pip install torch==2.0.1 torchvision==0.15.2 --index-url https://download.pytorch.org/whl/cpu -q 2>&1 | tail -3
        pip install tensorflow==2.12.0 -q 2>&1 | tail -3
        ok "Deep Learning CPU-only instalado."
    fi

    # Jupyter
    pip install jupyter==1.0.0 ipykernel==6.25.0 ipywidgets==8.1.0 -q 2>&1 | tail -3
    python3 -m ipykernel install --user --name odontoia-env --display-name "OdontoIA" 2>/dev/null || true
    ok "Jupyter Notebook configurado (kernel: OdontoIA)."

    # Testes
    pip install pytest==7.4.0 pytest-cov==4.1.0 -q 2>&1 | tail -3
    ok "pytest instalado."
}

#==============================================================================
# VERIFICAÇÃO DA INSTALAÇÃO
#==============================================================================
verify_installation() {
    info "Verificando instalação..."
    local erros=0

    # Testar importações essenciais
    python3 -c "
import numpy as np; print(f'numpy {np.__version__}: OK')
import pandas as pd; print(f'pandas {pd.__version__}: OK')
import sklearn; print(f'scikit-learn {sklearn.__version__}: OK')
import cv2; print(f'opencv {cv2.__version__}: OK')
import PIL; print(f'Pillow {PIL.__version__}: OK')
import matplotlib; print(f'matplotlib {matplotlib.__version__}: OK')
" 2>&1 | while read line; do ok "$line"; done

    # Deep Learning
    python3 -c "
import torch; print(f'PyTorch {torch.__version__}: OK')
print(f'  CUDA disponivel: {torch.cuda.is_available()}')
print(f'  Dispositivos: {torch.cuda.device_count() if torch.cuda.is_available() else 0}')
" 2>&1 | while read line; do ok "$line"; done

    python3 -c "
import tensorflow as tf; print(f'TensorFlow {tf.__version__}: OK')
print(f'  GPU disponivel: {len(tf.config.list_physical_devices(\"GPU\")) > 0}')
" 2>&1 | while read line; do ok "$line"; done

    info "Verificação concluída."
}

#==============================================================================
# PRINTSCREEN FINAL
#==============================================================================
print_summary() {
    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║  🦷 OdontoIA — Ambiente Instalado com Sucesso!             ║"
    echo "╠══════════════════════════════════════════════════════════════╣"
    echo "║  Para ativar o ambiente:                                   ║"
    echo "║    source odontoia-env/bin/activate                        ║"
    echo "║                                                            ║"
    echo "║  Para iniciar o Jupyter:                                   ║"
    echo "║    jupyter notebook                                        ║"
    echo "║                                                            ║"
    if [ "${GPU_AVAILABLE}" = true ]; then
        echo "║  ✅ GPU disponível — treinamento acelerado                ║"
    else
        echo "║  ⚠️  Modo CPU — use Google Colab para treinamentos         ║"
    fi
    echo "║                                                            ║"
    echo "║  Para desinstalar:                                         ║"
    echo "║    rm -rf odontoia-env/                                    ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
}

#==============================================================================
# MAIN
#==============================================================================
main() {
    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║     🦷 OdontoIA — Instalação do Ambiente                  ║"
    echo "║     Livro: Odontologia & Inteligência Artificial           ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""

    detect_os
    detect_gpu
    echo ""

    check_prerequisites || {
        erro "Pré-requisitos não satisfeitos. Corrija os erros acima e tente novamente."
        exit 1
    }
    echo ""

    install_system_deps
    echo ""

    setup_venv
    echo ""

    install_python_deps
    echo ""

    verify_installation
    echo ""

    print_summary
}

#==============================================================================
# PARSE DE ARGUMENTOS
#==============================================================================
FORCE_CPU=false
FORCE_GPU=false
VERIFY_ONLY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --cpu)     FORCE_CPU=true; shift ;;
        --gpu)     FORCE_GPU=true; GPU_AVAILABLE=true; shift ;;
        --verify)  VERIFY_ONLY=true; shift ;;
        --help|-h) 
            echo "Uso: bash apendice-d-instalacao.sh [OPÇÕES]"
            echo "  --cpu      Força instalação CPU-only"
            echo "  --gpu      Força instalação com CUDA"
            echo "  --verify   Apenas verifica instalação existente"
            echo "  --help     Mostra esta ajuda"
            exit 0
            ;;
        *) erro "Opção desconhecida: $1"; exit 1 ;;
    esac
done

if [ "${VERIFY_ONLY}" = true ]; then
    detect_os
    detect_gpu
    check_prerequisites
    verify_installation
    exit 0
fi

main
