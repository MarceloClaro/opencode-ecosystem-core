#!/usr/bin/env bash
# ============================================================================
# OpenCode Ecosystem Core — Provisioner WSL/Ubuntu
# ----------------------------------------------------------------------------
# Executado DENTRO do Ubuntu (WSL) pelo bootstrap PowerShell, ou manualmente:
#   bash provision.sh
#
# Instala: OpenCode CLI, Antigravity CLI, Ollama CLI, dependências do sistema
# e o repositório opencode-ecosystem-core (nativo no OpenCode CLI).
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
# 1. Dependências do sistema
# ---------------------------------------------------------------------------
log "Etapa 1/6: Atualizando pacotes do sistema (apt)..."
sudo apt-get update -y >>"$LOG_FILE" 2>&1
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y \
    git curl wget unzip zip ca-certificates \
    python3 python3-pip python3-venv \
    pandoc poppler-utils \
    build-essential >>"$LOG_FILE" 2>&1 \
  && ok "Dependências do sistema instaladas." \
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
# 2. OpenCode CLI
# ---------------------------------------------------------------------------
log "Etapa 2/6: Instalando OpenCode CLI..."
if command -v opencode >/dev/null 2>&1; then
    ok "OpenCode CLI já instalado: $(opencode --version 2>/dev/null | head -1)"
else
    curl -fsSL https://opencode.ai/install | bash >>"$LOG_FILE" 2>&1
    # O instalador coloca em ~/.opencode/bin ou ~/.local/bin
    export PATH="$HOME/.opencode/bin:$HOME/.local/bin:$PATH"
    if command -v opencode >/dev/null 2>&1; then
        ok "OpenCode CLI instalado: $(opencode --version 2>/dev/null | head -1)"
    else
        warn "Instalador oficial falhou; tentando fallback via npm..."
        sudo npm install -g opencode-ai@latest >>"$LOG_FILE" 2>&1 \
          && ok "OpenCode CLI instalado via npm." \
          || err "Falha ao instalar OpenCode CLI (verifique o log)."
    fi
fi

# ---------------------------------------------------------------------------
# 3. Antigravity CLI (agy)
# ---------------------------------------------------------------------------
log "Etapa 3/6: Instalando Antigravity CLI (agy)..."
if command -v agy >/dev/null 2>&1 || [ -x "$HOME/.local/bin/agy" ]; then
    ok "Antigravity CLI já instalado."
else
    curl -fsSL https://antigravity.google/cli/install.sh | bash >>"$LOG_FILE" 2>&1
    export PATH="$HOME/.local/bin:$PATH"
    if command -v agy >/dev/null 2>&1 || [ -x "$HOME/.local/bin/agy" ]; then
        ok "Antigravity CLI instalado em ~/.local/bin/agy"
    else
        err "Falha ao instalar Antigravity CLI (verifique conectividade/log)."
    fi
fi

# ---------------------------------------------------------------------------
# 4. Ollama CLI
# ---------------------------------------------------------------------------
log "Etapa 4/6: Instalando Ollama CLI..."
if command -v ollama >/dev/null 2>&1; then
    ok "Ollama já instalado: $(ollama --version 2>/dev/null | head -1)"
else
    curl -fsSL https://ollama.com/install.sh | sh >>"$LOG_FILE" 2>&1
    if command -v ollama >/dev/null 2>&1; then
        ok "Ollama instalado: $(ollama --version 2>/dev/null | head -1)"
    else
        err "Falha ao instalar Ollama (verifique o log)."
    fi
fi

# Garante que o serviço do Ollama esteja ativo (systemd no WSL2 moderno)
if command -v ollama >/dev/null 2>&1; then
    if command -v systemctl >/dev/null 2>&1 && systemctl is-system-running >/dev/null 2>&1; then
        sudo systemctl enable --now ollama >>"$LOG_FILE" 2>&1 || true
    fi
    if ! pgrep -f "ollama serve" >/dev/null 2>&1 && ! (command -v systemctl >/dev/null 2>&1 && systemctl is-active --quiet ollama 2>/dev/null); then
        nohup ollama serve >>"$LOG_FILE" 2>&1 &
        sleep 2
    fi
    ok "Serviço Ollama ativo."
fi

# ---------------------------------------------------------------------------
# 5. OpenCode Ecosystem Core (nativo)
# ---------------------------------------------------------------------------
log "Etapa 5/6: Instalando o OpenCode Ecosystem Core..."
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
log "Etapa 6/6: Configurando PATH, aliases e integração nativa..."
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
for tool in opencode agy ollama git python3 pandoc; do
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
