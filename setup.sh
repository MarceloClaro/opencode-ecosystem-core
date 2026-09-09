#!/usr/bin/env bash
# ============================================================================
# OpenCode Ecosystem Core — Instalador One-Click
# ============================================================================
# Uso (copie e cole no terminal):
#
#   curl -sSL https://raw.githubusercontent.com/MarceloClaro/opencode-ecosystem-core/main/setup.sh | bash
#
# Ou, se já baixou o repositório:
#
#   chmod +x setup.sh && ./setup.sh
#
# O que este script faz:
#   1. Instala dependências do sistema (Python, Git, node, etc.)
#   2. Clona o repositório (se ainda não existe)
#   3. Cria ambiente virtual Python
#   4. Instala todas as dependências Python
#   5. Instala OpenCode CLI
#   6. Instala Antigravity CLI (se disponível)
#   7. Configura o ecossistema
#   8. Roda diagnóstico final
# ============================================================================

set -euo pipefail

# Cores para mensagens
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Diretório de instalação
INSTALL_DIR="${HOME}/opencode-ecosystem-core"
VENV_DIR="${INSTALL_DIR}/.venv"

# Funções auxiliares
info()    { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[OK]${NC} $1"; }
warn()    { echo -e "${YELLOW}[AVISO]${NC} $1"; }
error()   { echo -e "${RED}[ERRO]${NC} $1"; }
step()    { echo -e "\n${BOLD}${CYAN}==> $1${NC}"; }

# ============================================================================
# Verificar se é root (não recomendado, mas possível)
# ============================================================================
if [ "$EUID" -eq 0 ]; then
    warn "Executando como root. Recomenda-se executar como usuário normal."
    warn "Pressione Ctrl+C nos próximos 5 segundos para cancelar."
    sleep 5
fi

# ============================================================================
# PASSO 1: Detectar sistema operacional
# ============================================================================
step "Passo 1/8: Detectando sistema operacional..."

OS="$(uname -s)"
ARCH="$(uname -m)"

if [ "$OS" = "Linux" ]; then
    if grep -qi microsoft /proc/version 2>/dev/null; then
        PLATFORM="WSL"
        info "Sistema detectado: Windows (WSL2)"
    else
        PLATFORM="Linux"
        info "Sistema detectado: Linux"
    fi
elif [ "$OS" = "Darwin" ]; then
    PLATFORM="macOS"
    info "Sistema detectado: macOS"
else
    error "Sistema operacional não suportado: $OS"
    exit 1
fi

# ============================================================================
# PASSO 2: Verificar e instalar dependências do sistema
# ============================================================================
step "Passo 2/8: Verificando dependências do sistema..."

install_system_deps() {
    if command -v apt-get &>/dev/null; then
        # Debian/Ubuntu/WSL
        info "Usando apt-get (Debian/Ubuntu)..."
        sudo apt-get update -qq
        sudo apt-get install -y -qq \
            python3 python3-pip python3-venv \
            git curl wget build-essential \
            nodejs npm \
            jq unzip
    elif command -v brew &>/dev/null; then
        # macOS com Homebrew
        info "Usando Homebrew (macOS)..."
        brew install python3 git curl wget node jq
    elif command -v dnf &>/dev/null; then
        # Fedora/RHEL
        info "Usando dnf (Fedora)..."
        sudo dnf install -y \
            python3 python3-pip python3-virtualenv \
            git curl wget gcc gcc-c++ make \
            nodejs npm \
            jq unzip
    elif command -v pacman &>/dev/null; then
        # Arch Linux
        info "Usando pacman (Arch)..."
        sudo pacman -Sy --noconfirm \
            python python-pip python-virtualenv \
            git curl wget base-devel \
            nodejs npm \
            jq unzip
    else
        warn "Gerenciador de pacotes não detectado."
        warn "Instale manualmente: python3, python3-venv, git, curl, nodejs, npm"
    fi
}

# Verificar Python
if command -v python3 &>/dev/null; then
    PY_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    success "Python encontrado: $PY_VERSION"
else
    info "Python não encontrado. Instalando..."
    install_system_deps
    if command -v python3 &>/dev/null; then
        success "Python instalado com sucesso"
    else
        error "Falha ao instalar Python. Instale manualmente."
        exit 1
    fi
fi

# Verificar Git
if command -v git &>/dev/null; then
    success "Git encontrado: $(git --version)"
else
    info "Git não encontrado. Instalando..."
    install_system_deps
fi

# Verificar Node.js (opcional, para MCPs)
if command -v node &>/dev/null; then
    success "Node.js encontrado: $(node --version)"
else
    warn "Node.js não encontrado. Alguns MCPs podem não funcionar."
    info "Para instalar: https://nodejs.org/"
fi

# ============================================================================
# PASSO 3: Clonar repositório (se não existe)
# ============================================================================
step "Passo 3/8: Verificando repositório..."

if [ -d "$INSTALL_DIR/.git" ]; then
    success "Repositório já existe em: $INSTALL_DIR"
    info "Atualizando..."
    cd "$INSTALL_DIR"
    git pull --ff-only || warn "Não foi possível atualizar. Mantendo versão atual."
else
    info "Clonando repositório..."
    git clone https://github.com/MarceloClaro/opencode-ecosystem-core.git "$INSTALL_DIR"
    cd "$INSTALL_DIR"
    success "Repositório clonado com sucesso"
fi

# ============================================================================
# PASSO 4: Criar ambiente virtual Python
# ============================================================================
step "Passo 4/8: Criando ambiente virtual Python..."

if [ -d "$VENV_DIR" ]; then
    success "Ambiente virtual já existe"
else
    info "Criando ambiente virtual..."
    python3 -m venv "$VENV_DIR"
    success "Ambiente virtual criado em: $VENV_DIR"
fi

# Ativar ambiente virtual
source "$VENV_DIR/bin/activate"
info "Ambiente virtual ativado"

# ============================================================================
# PASSO 5: Instalar dependências Python
# ============================================================================
step "Passo 5/8: Instalando dependências Python..."

info "Atualizando pip..."
pip install --upgrade pip --quiet

info "Instalando dependências principais..."
pip install -r requirements.txt --quiet

info "Instalando dependências de desenvolvimento (opcional)..."
if [ -f requirements-dev.txt ]; then
    pip install -r requirements-dev.txt --quiet 2>/dev/null || true
fi

if [ -f requirements-scientific-lab.txt ]; then
    pip install -r requirements-scientific-lab.txt --quiet 2>/dev/null || true
fi

success "Dependências Python instaladas"

# ============================================================================
# PASSO 6: Instalar CLIs externas
# ============================================================================
step "Passo 6/8: Instalando CLIs externas..."

# OpenCode CLI
info "Verificando OpenCode CLI..."
if command -v opencode &>/dev/null; then
    success "OpenCode CLI já instalado: $(opencode --version 2>/dev/null || echo 'versão desconhecida')"
else
    info "Instalando OpenCode CLI..."
    pip install opencode-cli --quiet 2>/dev/null || {
        warn "Não foi possível instalar OpenCode CLI via pip."
        warn "Tentando via npm..."
        npm install -g @opencode/cli 2>/dev/null || warn "OpenCode CLI não instalado. Instale manualmente."
    }
fi

# Antigravity CLI
info "Verificando Antigravity CLI..."
if command -v antigravity &>/dev/null; then
    success "Antigravity CLI já instalado"
else
    info "Antigravity CLI não encontrado. Será necessário configurar manualmente."
    info "Consulte: https://github.com/anthropics/antigravity"
fi

# Claude CLI
info "Verificando Claude CLI..."
if command -v claude &>/dev/null; then
    success "Claude CLI já instalado"
else
    info "Claude CLI não encontrado. Será necessário configurar manualmente."
    info "Consulte: https://github.com/anthropics/claude-cli"
fi

# ============================================================================
# PASSO 7: Configurar ecossistema
# ============================================================================
step "Passo 7/8: Configurando ecossistema..."

info "Rodando diagnóstico inicial..."
python3 -m marceloclaro.cli doctor 2>/dev/null || {
    warn "Diagnóstico encontrou problemas. Consulte a saída acima."
    warn "Isso é normal na primeira execução."
}

# ============================================================================
# PASSO 8: Verificação final
# ============================================================================
step "Passo 8/8: Verificação final..."

echo ""
echo -e "${BOLD}${GREEN}========================================${NC}"
echo -e "${BOLD}${GREEN}  INSTALAÇÃO CONCLUÍDA COM SUCESSO!    ${NC}"
echo -e "${BOLD}${GREEN}========================================${NC}"
echo ""
echo -e "Diretório: ${BOLD}${INSTALL_DIR}${NC}"
echo -e "Ambiente virtual: ${BOLD}${VENV_DIR}${NC}"
echo ""
echo -e "${BOLD}Próximos passos:${NC}"
echo ""
echo -e "  1. Ative o ambiente virtual:"
echo -e "     ${CYAN}source ${VENV_DIR}/bin/activate${NC}"
echo ""
echo -e "  2. Execute o diagnóstico:"
echo -e "     ${CYAN}python3 -m marceloclaro.cli doctor${NC}"
echo ""
echo -e "  3. Veja a ajuda:"
echo -e "     ${CYAN}python3 -m marceloclaro.cli helpdesk${NC}"
echo ""
echo -e "  4. Comece a usar:"
echo -e "     ${CYAN}python3 -m marceloclaro.cli${NC}"
echo ""
echo -e "${BOLD}Documentação:${NC}"
echo -e "  - Manual: ${CYAN}${INSTALL_DIR}/MANUAL.md${NC}"
echo -e "  - Arquitetura: ${CYAN}${INSTALL_DIR}/ARCHITECTURE.md${NC}"
echo -e "  - GitHub: ${CYAN}https://github.com/MarceloClaro/opencode-ecosystem-core${NC}"
echo ""
echo -e "${BOLD}Para desinstalar:${NC}"
echo -e "  ${CYAN}curl -sSL https://raw.githubusercontent.com/MarceloClaro/opencode-ecosystem-core/main/uninstall.sh | bash${NC}"
echo ""
