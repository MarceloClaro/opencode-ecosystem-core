#!/usr/bin/env bash
# ============================================================================
# OpenCode Ecosystem Core — Instalador para macOS (BEST-EFFORT)
# ----------------------------------------------------------------------------
# AVISO: este script não foi testado em hardware Apple real — foi escrito
# por analogia ao instalador Linux nativo e ao provisionador WSL, usando
# Homebrew como gerenciador de pacotes. Reporte problemas em issues do
# repositório. `python3 -m marceloclaro.cli doctor` sinaliza este caminho
# como best-effort.
#
# Uso:
#   curl -fsSL https://raw.githubusercontent.com/MarceloClaro/opencode-ecosystem-core/main/installer/macos/install.sh | bash
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
echo "  OpenCode Ecosystem Core — Instalador macOS (BEST-EFFORT)"
echo "  Nao testado em hardware Apple real. Log: $LOG_FILE"
echo "==================================================================="

# ---------------------------------------------------------------------------
# 1. Dependências (Homebrew)
# ---------------------------------------------------------------------------
log "Etapa 1/4: Instalando dependências do sistema (Homebrew)..."
if ! command -v brew >/dev/null 2>&1; then
    warn "Homebrew não encontrado — instalando..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" >>"$LOG_FILE" 2>&1 \
      || { err "Falha ao instalar Homebrew. Instale manualmente: https://brew.sh"; }
fi
if command -v brew >/dev/null 2>&1; then
    brew install git python3 node pandoc poppler zstd >>"$LOG_FILE" 2>&1 \
      && ok "Dependências instaladas via Homebrew." \
      || warn "Alguns pacotes brew falharam (veja o log); prosseguindo."
else
    warn "Homebrew indisponível — instale manualmente: git, python3, node, pandoc, poppler."
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
    git -C "$ECO_DIR" pull --ff-only >>"$LOG_FILE" 2>&1 && ok "Ecosystem atualizado." || warn "git pull falhou; mantendo versão local."
else
    git clone --depth 1 "$REPO_URL" "$ECO_DIR" >>"$LOG_FILE" 2>&1
    [ -d "$ECO_DIR/.git" ] && ok "Ecosystem clonado em $ECO_DIR" || err "Falha ao clonar $REPO_URL."
fi

if [ -f "$ECO_DIR/requirements.txt" ]; then
    pip3 install --user -q -r "$ECO_DIR/requirements.txt" >>"$LOG_FILE" 2>&1 \
      || warn "Falha parcial ao instalar requirements Python."
    ok "Dependências Python do ecossistema instaladas."
fi
pip3 install --user -q pymupdf pymupdf4llm pypdf sympy z3-solver >>"$LOG_FILE" 2>&1 || true

if command -v python3 >/dev/null 2>&1 && [ -f "$ECO_DIR/assets/generate_icon.py" ]; then
    (cd "$ECO_DIR" && python3 assets/generate_icon.py >>"$LOG_FILE" 2>&1) && ok "Ícone gerado (.png/.ico + iconset)." || warn "Falha ao gerar ícone (Pillow ausente?)."
    if [ -d "$ECO_DIR/assets/icon.iconset" ] && command -v iconutil >/dev/null 2>&1; then
        bash "$SCRIPT_DIR/build_icns.sh" >>"$LOG_FILE" 2>&1 && ok "icon.icns gerado (iconutil)." || warn "Falha ao gerar icon.icns."
    fi
fi

# ---------------------------------------------------------------------------
# 4. PATH, aliases, integração nativa e launcher (.command)
# ---------------------------------------------------------------------------
log "Etapa 4/4: Configurando PATH, aliases, integração nativa e atalho..."
SHELL_RC="$HOME/.zshrc"
[ -n "${BASH_VERSION:-}" ] && [ -f "$HOME/.bash_profile" ] && SHELL_RC="$HOME/.bash_profile"
add_line() { grep -qxF "$1" "$SHELL_RC" 2>/dev/null || echo "$1" >> "$SHELL_RC"; }
add_line 'export PATH="$HOME/.opencode/bin:$HOME/.local/bin:$PATH"'
add_line "alias ecosystem='cd $ECO_DIR && python3 -m marceloclaro.cli'"

if [ -f "$ECO_DIR/integrations/opencode_cli.py" ]; then
    (cd "$ECO_DIR" && python3 -c "
from integrations.opencode_cli import OpenCodeCLIIntegration
OpenCodeCLIIntegration('.').generate_config()
" >>"$LOG_FILE" 2>&1) && ok "Integração nativa OpenCode CLI configurada." \
      || warn "Não foi possível regenerar opencode.json."
fi

# Launcher .command (duplo-clique abre o Terminal.app) — alternativa
# prática a um .app bundle completo, que exigiria assinatura/notarização.
DESKTOP_DIR="$HOME/Desktop"
if [ -d "$DESKTOP_DIR" ]; then
    LAUNCHER="$DESKTOP_DIR/Ecosystem (marceloclaro).command"
    cat > "$LAUNCHER" <<EOF
#!/usr/bin/env bash
cd "$ECO_DIR" && python3 -m marceloclaro.cli
EOF
    chmod +x "$LAUNCHER"
    ok "Launcher criado: $LAUNCHER (duplo-clique para abrir)"
else
    warn "Área de Trabalho (~/Desktop) não encontrada; launcher não criado."
fi

# ---------------------------------------------------------------------------
# Smoke tests
# ---------------------------------------------------------------------------
echo ""
echo "==================================================================="
echo "  VERIFICAÇÃO FINAL"
echo "==================================================================="
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
    ok "Instalação concluída! (best-effort — reporte problemas específicos de macOS)"
else
    warn "Instalação concluída com pendências. Revise: $LOG_FILE"
fi
echo "Para desinstalar: bash $ECO_DIR/installer/macos/uninstall.sh"
exit 0
