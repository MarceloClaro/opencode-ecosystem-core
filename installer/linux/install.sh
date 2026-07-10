#!/usr/bin/env bash
# ============================================================================
# OpenCode Ecosystem Core — Instalador nativo para Linux (sem WSL)
# ----------------------------------------------------------------------------
# Uso:
#   curl -fsSL https://raw.githubusercontent.com/MarceloClaro/opencode-ecosystem-core/main/installer/linux/install.sh | bash
# Ou, com o repositório já clonado:
#   bash installer/linux/install.sh
#
# Caminho principal testado: distros baseadas em Debian/Ubuntu (apt-get).
# Outras distros (Fedora/Arch/openSUSE) recebem um aviso claro e a
# instalação prossegue best-effort (dependências de sistema podem faltar).
# Idempotente: pode ser reexecutado com segurança para atualizar tudo.
# ============================================================================
set -uo pipefail

REPO_URL="${ECOSYSTEM_REPO_URL:-https://github.com/MarceloClaro/opencode-ecosystem-core.git}"
ECO_DIR="${ECOSYSTEM_DIR:-$HOME/opencode-ecosystem-core}"
LOG_FILE="$HOME/.opencode-ecosystem-install.log"

C_GREEN='\033[0;32m'; C_YELLOW='\033[1;33m'; C_RED='\033[0;31m'; C_CYAN='\033[0;36m'; C_OFF='\033[0m'
log()  { echo -e "${C_CYAN}[ECOSYSTEM]${C_OFF} $*" | tee -a "$LOG_FILE"; }
ok()   { echo -e "${C_GREEN}[OK]${C_OFF} $*"       | tee -a "$LOG_FILE"; }
warn() { echo -e "${C_YELLOW}[AVISO]${C_OFF} $*"   | tee -a "$LOG_FILE"; }
err()  { echo -e "${C_RED}[ERRO]${C_OFF} $*"       | tee -a "$LOG_FILE"; }

echo "==================================================================="
echo "  OpenCode Ecosystem Core — Instalador Linux Nativo"
echo "  Log: $LOG_FILE"
echo "==================================================================="

# ---------------------------------------------------------------------------
# 1. Dependências do sistema
# ---------------------------------------------------------------------------
log "Etapa 1/4: Instalando dependências do sistema..."
if command -v apt-get >/dev/null 2>&1; then
    sudo apt-get update -y >>"$LOG_FILE" 2>&1
    sudo DEBIAN_FRONTEND=noninteractive apt-get install -y \
        git curl wget unzip zip ca-certificates \
        python3 python3-pip python3-venv \
        pandoc poppler-utils build-essential zstd \
        nodejs npm >>"$LOG_FILE" 2>&1 \
      && ok "Dependências do sistema instaladas (apt)." \
      || warn "Alguns pacotes apt falharam (veja o log); prosseguindo."
elif command -v dnf >/dev/null 2>&1; then
    warn "Distro baseada em Fedora/RHEL detectada — caminho best-effort (menos testado que Debian/Ubuntu)."
    sudo dnf install -y git curl wget unzip zip python3 python3-pip pandoc poppler-utils \
        gcc gcc-c++ make nodejs npm zstd >>"$LOG_FILE" 2>&1 \
      && ok "Dependências do sistema instaladas (dnf)." \
      || warn "Alguns pacotes dnf falharam (veja o log); prosseguindo."
elif command -v pacman >/dev/null 2>&1; then
    warn "Distro baseada em Arch detectada — caminho best-effort (menos testado que Debian/Ubuntu)."
    sudo pacman -Sy --noconfirm git curl wget unzip zip python python-pip pandoc poppler \
        base-devel nodejs npm zstd >>"$LOG_FILE" 2>&1 \
      && ok "Dependências do sistema instaladas (pacman)." \
      || warn "Alguns pacotes pacman falharam (veja o log); prosseguindo."
else
    warn "Gerenciador de pacotes não reconhecido (apt/dnf/pacman) — instale manualmente: git, curl, python3, pip, pandoc, poppler-utils, node, npm."
fi

# ---------------------------------------------------------------------------
# 2. CLIs externas (OpenCode, Antigravity, Claude Code, Ollama)
# ---------------------------------------------------------------------------
log "Etapa 2/4: Instalando CLIs externas..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMMON_LIB="$SCRIPT_DIR/../common/install_clis.sh"
if [ ! -f "$COMMON_LIB" ]; then
    COMMON_LIB="/tmp/opencode-ecosystem-install_clis.sh"
    curl -fsSL "https://raw.githubusercontent.com/MarceloClaro/opencode-ecosystem-core/main/installer/common/install_clis.sh" \
        -o "$COMMON_LIB" 2>>"$LOG_FILE" || warn "Não foi possível baixar install_clis.sh; instalação de CLIs pode falhar."
fi
# shellcheck source=/dev/null
source "$COMMON_LIB"
install_opencode_cli
install_antigravity_cli
install_claude_code_cli
install_ollama_cli

# ---------------------------------------------------------------------------
# 3. OpenCode Ecosystem Core
# ---------------------------------------------------------------------------
log "Etapa 3/4: Instalando o OpenCode Ecosystem Core..."
if [ -d "$ECO_DIR/.git" ]; then
    log "Repositório já existe; atualizando (git pull)..."
    git -C "$ECO_DIR" pull --ff-only >>"$LOG_FILE" 2>&1 && ok "Ecosystem atualizado." || warn "git pull falhou; mantendo versão local."
else
    git clone --depth 1 "$REPO_URL" "$ECO_DIR" >>"$LOG_FILE" 2>&1
    if [ -d "$ECO_DIR/.git" ]; then
        ok "Ecosystem clonado em $ECO_DIR"
    else
        err "Falha ao clonar $REPO_URL."
        err "Se o repositório for PRIVADO, autentique primeiro: gh auth login"
    fi
fi

if [ -f "$ECO_DIR/requirements.txt" ]; then
    pip3 install --user --break-system-packages -q -r "$ECO_DIR/requirements.txt" >>"$LOG_FILE" 2>&1 \
      || pip3 install --user -q -r "$ECO_DIR/requirements.txt" >>"$LOG_FILE" 2>&1 \
      || warn "Falha parcial ao instalar requirements Python."
    ok "Dependências Python do ecossistema instaladas."
fi
pip3 install --user --break-system-packages -q pymupdf pymupdf4llm pypdf sympy z3-solver >>"$LOG_FILE" 2>&1 || true

if command -v python3 >/dev/null 2>&1 && [ -f "$ECO_DIR/assets/generate_icon.py" ]; then
    (cd "$ECO_DIR" && python3 assets/generate_icon.py >>"$LOG_FILE" 2>&1) && ok "Ícone gerado." || warn "Falha ao gerar ícone (Pillow ausente?)."
fi

# ---------------------------------------------------------------------------
# 4. PATH, aliases, integração nativa e launcher (.desktop)
# ---------------------------------------------------------------------------
log "Etapa 4/4: Configurando PATH, aliases, integração nativa e atalho..."
SHELL_RC="$HOME/.bashrc"
[ -n "${ZSH_VERSION:-}" ] && SHELL_RC="$HOME/.zshrc"
add_line() { grep -qxF "$1" "$SHELL_RC" 2>/dev/null || echo "$1" >> "$SHELL_RC"; }

add_line 'export PATH="$HOME/.opencode/bin:$HOME/.local/bin:$PATH"'
add_line "alias ecosystem='cd $ECO_DIR && python3 -m marceloclaro.cli'"
add_line "alias eco-opencode='cd $ECO_DIR && opencode'"
add_line "alias eco-agy='cd $ECO_DIR && agy'"
add_line "alias eco-claude='cd $ECO_DIR && claude'"

if [ -f "$ECO_DIR/integrations/opencode_cli.py" ]; then
    (cd "$ECO_DIR" && python3 -c "
from integrations.opencode_cli import OpenCodeCLIIntegration
integ = OpenCodeCLIIntegration('.')
path = integ.generate_config()
print(f'opencode.json regenerado: {path}')
" >>"$LOG_FILE" 2>&1) && ok "Integração nativa OpenCode CLI configurada." \
      || warn "Não foi possível regenerar opencode.json (usando o do repositório)."
fi

# Launcher .desktop (padrão freedesktop.org — funciona em GNOME/KDE/XFCE...)
DESKTOP_FILE_DIR="$HOME/.local/share/applications"
mkdir -p "$DESKTOP_FILE_DIR"
ICON_PATH="$ECO_DIR/assets/icon.png"
cat > "$DESKTOP_FILE_DIR/opencode-ecosystem.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Ecosystem (marceloclaro)
Comment=CLI interativo do orquestrador metacognitivo marceloclaro
Exec=x-terminal-emulator -e bash -lic "cd $ECO_DIR && python3 -m marceloclaro.cli"
Icon=$ICON_PATH
Terminal=true
Categories=Development;
EOF
chmod +x "$DESKTOP_FILE_DIR/opencode-ecosystem.desktop"
ok "Launcher criado em $DESKTOP_FILE_DIR/opencode-ecosystem.desktop"

# Copia também para a Área de Trabalho, se existir
for candidate in "$HOME/Desktop" "$HOME/Área de Trabalho" "$HOME/Escritorio"; do
    if [ -d "$candidate" ]; then
        cp "$DESKTOP_FILE_DIR/opencode-ecosystem.desktop" "$candidate/" 2>/dev/null
        chmod +x "$candidate/opencode-ecosystem.desktop" 2>/dev/null
        ok "Atalho copiado para $candidate"
        break
    fi
done

# ---------------------------------------------------------------------------
# Smoke tests
# ---------------------------------------------------------------------------
echo ""
echo "==================================================================="
echo "  VERIFICAÇÃO FINAL"
echo "==================================================================="
export PATH="$HOME/.opencode/bin:$HOME/.local/bin:$PATH"
FAIL=0
for tool in opencode agy claude ollama git python3 pandoc; do
    if command -v "$tool" >/dev/null 2>&1; then
        ok "$tool disponível."
    else
        err "$tool NÃO encontrado."
        FAIL=1
    fi
done

if [ -d "$ECO_DIR" ] && (cd "$ECO_DIR" && python3 -c "from marceloclaro.orchestrator import MarceloClaroOrchestrator" 2>>"$LOG_FILE"); then
    ok "Ecossistema importável (orquestrador marceloclaro OK)."
else
    err "Ecossistema não importável — verifique $LOG_FILE."
    FAIL=1
fi

echo ""
if [ "$FAIL" -eq 0 ]; then
    ok "Instalação concluída com sucesso! Abra um novo terminal e rode: ecosystem"
else
    warn "Instalação concluída com pendências. Revise: $LOG_FILE"
fi
echo "Para desinstalar: bash $ECO_DIR/installer/linux/uninstall.sh"
exit 0
