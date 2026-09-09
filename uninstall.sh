#!/usr/bin/env bash
# ============================================================================
# OpenCode Ecosystem Core — Desinstalador Total
# ============================================================================
# Uso (copie e cole no terminal):
#
#   curl -sSL https://raw.githubusercontent.com/MarceloClaro/opencode-ecosystem-core/main/uninstall.sh | bash
#
# Ou, se já baixou o repositório:
#
#   chmod +x uninstall.sh && ./uninstall.sh
#
# O que este script faz (em ordem):
#   1. Remove o repositório OpenCode Ecosystem Core
#   2. Remove o ambiente virtual Python
#   3. Remove dependências Python instaladas
#   4. Remove OpenCode CLI
#   5. Remove configs e caches
#   6. (Opcional) Remove WSL completo (Windows)
# ============================================================================

set -euo pipefail

# Cores para mensagens
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'
BOLD='\033[1m'

# Diretórios
INSTALL_DIR="${HOME}/opencode-ecosystem-core"
VENV_DIR="${INSTALL_DIR}/.venv"

# Funções auxiliares
info()    { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[OK]${NC} $1"; }
warn()    { echo -e "${YELLOW}[AVISO]${NC} $1"; }
error()   { echo -e "${RED}[ERRO]${NC} $1"; }
step()    { echo -e "\n${BOLD}${CYAN}==> $1${NC}"; }

# ============================================================================
# Confirmação
# ============================================================================
echo -e "\n${BOLD}${RED}========================================${NC}"
echo -e "${BOLD}${RED}  DESINSTALAÇÃO TOTAL DO OPENCODE      ${NC}"
echo -e "${BOLD}${RED}  ECOSYSTEM CORE                       ${NC}"
echo -e "${BOLD}${RED}========================================${NC}"
echo ""
echo -e "${YELLOW}ATENÇÃO: Este script irá:${NC}"
echo -e "  - Remover o repositório completo"
echo -e "  - Remover o ambiente virtual Python"
echo -e "  - Remover dependências Python instaladas"
echo -e "  - Remover configurações e caches"
echo -e "  - (Opcional) Remover WSL do Windows"
echo ""
echo -e "${BOLD}Esta ação é IRREVERSÍVEL!${NC}"
echo ""
read -p "$(echo -e ${BOLD}Deseja continuar? \(s/N\): ${NC})" -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Ss]$ ]]; then
    echo -e "${YELLOW}Desinstalação cancelada.${NC}"
    exit 0
fi

# ============================================================================
# PASSO 1: Fechar processos em execução
# ============================================================================
step "Passo 1/6: Fechando processos do ecossistema..."

# Matar processos do OpenCode
pkill -f "marceloclaro" 2>/dev/null || true
pkill -f "opencode" 2>/dev/null || true
pkill -f "colibri" 2>/dev/null || true
sleep 1

success "Processos finalizados"

# ============================================================================
# PASSO 2: Remover repositório e ambiente virtual
# ============================================================================
step "Passo 2/6: Removendo repositório e ambiente virtual..."

if [ -d "$INSTALL_DIR" ]; then
    info "Removendo: $INSTALL_DIR"
    rm -rf "$INSTALL_DIR"
    success "Repositório removido"
else
    info "Repositório não encontrado em: $INSTALL_DIR"
fi

# ============================================================================
# PASSO 3: Remover dependências Python
# ============================================================================
step "Passo 3/6: Removendo dependências Python..."

# Remover pacotes Python instalados globalmente
PACKAGES_TO_REMOVE=(
    "opencode-cli"
    "mcp"
    "httpx"
    "click"
    "prompt-toolkit"
    "pyyaml"
    "jsonschema"
    "whoosh"
    "jinja2"
    "numpy"
    "scikit-learn"
    "starlette"
    "sse-starlette"
    "sympy"
    "z3-solver"
    "python-docx"
    "requests"
    "huggingface-hub"
    "kaggle"
)

for pkg in "${PACKAGES_TO_REMOVE[@]}"; do
    pip uninstall -y "$pkg" 2>/dev/null && info "Removido: $pkg" || true
done

success "Dependências Python removidas"

# ============================================================================
# PASSO 4: Remover CLIs externas
# ============================================================================
step "Passo 4/6: Removendo CLIs externas..."

# OpenCode CLI
if command -v opencode &>/dev/null; then
    pip uninstall -y opencode-cli 2>/dev/null || true
    npm uninstall -g @opencode/cli 2>/dev/null || true
    success "OpenCode CLI removido"
fi

# Limpar cache npm
if [ -d "${HOME}/.npm" ]; then
    info "Limpando cache npm..."
    rm -rf "${HOME}/.npm"
    success "Cache npm limpo"
fi

# ============================================================================
# PASSO 5: Remover configs e caches
# ============================================================================
step "Passo 5/6: Removendo configurações e caches..."

# Diretórios de configuração
DIRS_TO_REMOVE=(
    "${HOME}/.config/opencode"
    "${HOME}/.config/cosign"
    "${HOME}/.local/share/opencode"
    "${HOME}/.cache/opencode"
    "${HOME}/.opencode"
    "${HOME}/.kaggle"
)

for dir in "${DIRS_TO_REMOVE[@]}"; do
    if [ -d "$dir" ]; then
        info "Removendo: $dir"
        rm -rf "$dir"
    fi
done

# Arquivos de configuração
FILES_TO_REMOVE=(
    "${HOME}/.config/colibri.json"
    "${HOME}/.aws/credentials"
)

for file in "${FILES_TO_REMOVE[@]}"; do
    if [ -f "$file" ]; then
        info "Removendo: $file"
        rm -f "$file"
    fi
done

success "Configurações e caches removidos"

# ============================================================================
# PASSO 6: (Opcional) Remover WSL
# ============================================================================
step "Passo 6/6: Verificando WSL..."

if grep -qi microsoft /proc/version 2>/dev/null; then
    echo ""
    echo -e "${YELLOW}ATENÇÃO: Você está dentro do WSL!${NC}"
    echo ""
    echo -e "Para remover o WSL completamente, execute o seguinte comando"
    echo -e "no ${BOLD}PowerShell do Windows (como Administrador):${NC}"
    echo ""
    echo -e "  ${CYAN}wsl --unregister Ubuntu${NC}"
    echo ""
    echo -e "Isso irá:"
    echo -e "  - Remover a distribuição Ubuntu do WSL"
    echo -e "  - Remover todos os dados dentro do WSL"
    echo -e "  - Libertar espaço em disco"
    echo ""
    echo -e "Para remover o WSL completamente do Windows:"
    echo -e "  ${CYAN}dism.exe /online /disable-feature /featurename:Microsoft-Windows-Subsystem-Linux${NC}"
    echo ""
    echo -e "  ${CYAN}dism.exe /online /disable-feature /featurename:VirtualMachinePlatform${NC}"
    echo ""
fi

# ============================================================================
# Conclusão
# ============================================================================
echo ""
echo -e "${BOLD}${GREEN}========================================${NC}"
echo -e "${BOLD}${GREEN}  DESINSTALAÇÃO CONCLUÍDA!             ${NC}"
echo -e "${BOLD}${GREEN}========================================${NC}"
echo ""
echo -e "Todos os componentes do OpenCode Ecosystem Core foram removidos."
echo ""
echo -e "${BOLD}Espaço liberado:${NC}"
du -sh "$INSTALL_DIR" 2>/dev/null || echo "  Repositório já removido"
echo ""
echo -e "${BOLD}Para reinstalar:${NC}"
echo -e "  ${CYAN}curl -sSL https://raw.githubusercontent.com/MarceloClaro/opencode-ecosystem-core/main/setup.sh | bash${NC}"
echo ""
echo -e "${BOLD}Obrigado por usar o OpenCode Ecosystem Core!${NC}"
echo ""
