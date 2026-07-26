#!/usr/bin/env bash
# ============================================================================
# OpenCode Ecosystem Core — Provisioner WSL/Ubuntu
# ----------------------------------------------------------------------------
# Executado DENTRO do Ubuntu (WSL) pelo bootstrap PowerShell, ou manualmente:
#   bash provision.sh
#
# Instala: OpenCode CLI, Antigravity CLI, Claude Code CLI, Ollama CLI,
# dependências do sistema e o repositório opencode-ecosystem-core
# (nativo no OpenCode CLI).
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
echo "  OpenCode Ecosystem Core — Provisionamento do Ubuntu (WSL)"
echo "  Log: $LOG_FILE"
echo "==================================================================="

# ---------------------------------------------------------------------------
# 0. Garante sudo sem senha para este usuário (idempotente)
# ---------------------------------------------------------------------------
CURRENT_USER="$(whoami)"
SUDOERS_FILE="/etc/sudoers.d/opencode-ecosystem-nopasswd"
if [ ! -f "$SUDOERS_FILE" ] || ! grep -q "$CURRENT_USER" "$SUDOERS_FILE" 2>/dev/null; then
    log "Configurando sudo NOPASSWD para '$CURRENT_USER' (necessário para instalação automática)..."
    echo "$CURRENT_USER ALL=(ALL) NOPASSWD:ALL" | sudo tee "$SUDOERS_FILE" > /dev/null 2>&1 && \
        sudo chmod 440 "$SUDOERS_FILE" && \
        ok "sudo NOPASSWD configurado. Próximas execuções não pedirão senha." || \
        warn "Não foi possível configurar sudoers automaticamente. Sudo pode pedir senha."
else
    ok "sudo NOPASSWD já configurado para '$CURRENT_USER'."
fi

# ---------------------------------------------------------------------------
# 1. Dependências do sistema
#    Inclui zstd (obrigatório desde Ollama v0.4+ para extração do binário)
# ---------------------------------------------------------------------------
log "Etapa 1/4: Atualizando pacotes do sistema (apt)..."
sudo apt-get update -y >>"$LOG_FILE" 2>&1
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y \
    git curl wget unzip zip ca-certificates \
    python3 python3-pip python3-venv \
    pandoc poppler-utils \
    build-essential \
    zstd >>"$LOG_FILE" 2>&1 \
  && ok "Dependências do sistema instaladas (incluindo zstd)." \
  || warn "Alguns pacotes apt falharam (veja o log); prosseguindo."

# Node.js (necessário para fallback npm do OpenCode e ferramentas mermaid)
if ! command -v node >/dev/null 2>&1; then
    log "Instalando Node.js 22 (NodeSource)..."
    curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash - >>"$LOG_FILE" 2>&1
    sudo apt-get install -y nodejs >>"$LOG_FILE" 2>&1 && ok "Node.js instalado: $(node --version)"
else
    ok "Node.js já presente: $(node --version)"
fi

# ---------------------------------------------------------------------------
# 2-4. CLIs externas: OpenCode, Antigravity (agy), Claude Code, Ollama
#      (lógica compartilhada com installer/linux/install.sh e
#      installer/macos/install.sh — ver installer/common/install_clis.sh)
# ---------------------------------------------------------------------------
log "Etapa 2/4: Instalando CLIs externas (OpenCode, Antigravity, Claude Code, Ollama)..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMMON_LIB="$SCRIPT_DIR/../common/install_clis.sh"
if [ ! -f "$COMMON_LIB" ]; then
    # Execução isolada: baixa a biblioteca compartilhada quando necessário.
    COMMON_LIB="/tmp/opencode-ecosystem-install_clis.sh"
    curl -fsSL "https://raw.githubusercontent.com/MarceloClaro/opencode-ecosystem-core/main/installer/common/install_clis.sh" \
        -o "$COMMON_LIB" 2>>"$LOG_FILE" || \
        warn "Não foi possível baixar install_clis.sh; instalação de CLIs pode falhar."
fi
# shellcheck source=/dev/null
source "$COMMON_LIB"

install_opencode_cli
install_antigravity_cli
install_claude_code_cli
install_ollama_cli

# ---------------------------------------------------------------------------
# 5. OpenCode Ecosystem Core (nativo)
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
        err "Se o repositório for PRIVADO, autentique primeiro:  gh auth login  (ou use um token: git clone https://<TOKEN>@github.com/MarceloClaro/opencode-ecosystem-core.git)"
    fi
fi

if [ -f "$ECO_DIR/requirements.txt" ]; then
    pip3 install --user --break-system-packages -q -r "$ECO_DIR/requirements.txt" >>"$LOG_FILE" 2>&1 \
      || pip3 install --user -q -r "$ECO_DIR/requirements.txt" >>"$LOG_FILE" 2>&1 \
      || warn "Falha parcial ao instalar requirements Python."
    ok "Dependências Python do ecossistema instaladas."
fi

# Pacotes Python extras usados pelos subsistemas (best-effort)
pip3 install --user --break-system-packages -q pymupdf pymupdf4llm pypdf sympy z3-solver >>"$LOG_FILE" 2>&1 || true

# ---------------------------------------------------------------------------
# 6. PATH, aliases e integração nativa
# ---------------------------------------------------------------------------
log "Etapa 4/4: Configurando PATH, aliases e integração nativa..."
BASHRC="$HOME/.bashrc"
add_line() { grep -qxF "$1" "$BASHRC" 2>/dev/null || echo "$1" >> "$BASHRC"; }

add_line 'export PATH="$HOME/.opencode/bin:$HOME/.local/bin:$PATH"'
add_line "alias ecosystem='cd $ECO_DIR && python3 -m marceloclaro.cli'"
add_line "alias eco-opencode='cd $ECO_DIR && opencode'"
add_line "alias eco-agy='cd $ECO_DIR && agy'"

# Integração nativa: o opencode.json do repositório carrega os agentes e o
# servidor MCP metacognitivo automaticamente quando o OpenCode CLI é aberto
# dentro da pasta do ecossistema. Regenera para garantir paths corretos:
if [ -f "$ECO_DIR/integrations/opencode_cli.py" ]; then
    (cd "$ECO_DIR" && python3 -c "
from integrations.opencode_cli import OpenCodeCLIIntegration
integ = OpenCodeCLIIntegration('.')
path = integ.generate_config()
print(f'opencode.json regenerado: {path}')
" >>"$LOG_FILE" 2>&1) && ok "Integração nativa OpenCode CLI configurada." \
      || warn "Não foi possível regenerar opencode.json (usando o do repositório)."
fi

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
    ok "Provisionamento concluído com sucesso!"
else
    warn "Provisionamento concluído com pendências. Revise: $LOG_FILE"
fi
exit 0
