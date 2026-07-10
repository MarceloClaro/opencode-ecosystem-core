#!/usr/bin/env bash
# ============================================================================
# OpenCode Ecosystem Core — Instalação compartilhada das CLIs externas
# ----------------------------------------------------------------------------
# Biblioteca de funções bash (NÃO é um script executável sozinho — precisa
# ser `source`ado) com a lógica de instalar OpenCode CLI, Antigravity CLI
# (agy), Ollama CLI e Claude Code CLI. Usada por:
#   - installer/windows/provision.sh   (dentro do WSL/Ubuntu)
#   - installer/linux/install.sh       (Linux nativo)
#   - installer/macos/install.sh       (macOS, best-effort)
#
# Evita duplicar a mesma lógica de instalação em 3 lugares diferentes.
#
# Requer que o script chamador já tenha definido (ou aceita os defaults
# abaixo): as funções log()/ok()/warn()/err() e a variável $LOG_FILE.
# ============================================================================

# Defaults de logging, caso o script chamador ainda não os tenha definido.
declare -f log  >/dev/null 2>&1 || log()  { echo "[ECOSYSTEM] $*"; }
declare -f ok   >/dev/null 2>&1 || ok()   { echo "[OK] $*"; }
declare -f warn >/dev/null 2>&1 || warn() { echo "[AVISO] $*"; }
declare -f err  >/dev/null 2>&1 || err()  { echo "[ERRO] $*"; }
: "${LOG_FILE:=/tmp/opencode-ecosystem-install-clis.log}"

# ---------------------------------------------------------------------------
install_opencode_cli() {
    log "Instalando OpenCode CLI..."
    if command -v opencode >/dev/null 2>&1; then
        ok "OpenCode CLI já instalado: $(opencode --version 2>/dev/null | head -1)"
        return 0
    fi
    curl -fsSL https://opencode.ai/install | bash >>"$LOG_FILE" 2>&1
    export PATH="$HOME/.opencode/bin:$HOME/.local/bin:$PATH"
    if command -v opencode >/dev/null 2>&1; then
        ok "OpenCode CLI instalado: $(opencode --version 2>/dev/null | head -1)"
        return 0
    fi
    warn "Instalador oficial do OpenCode falhou; tentando fallback via npm..."
    if command -v npm >/dev/null 2>&1; then
        (command -v sudo >/dev/null 2>&1 && sudo npm install -g opencode-ai@latest || npm install -g opencode-ai@latest) >>"$LOG_FILE" 2>&1 \
            && ok "OpenCode CLI instalado via npm." \
            || { err "Falha ao instalar OpenCode CLI (verifique o log)."; return 1; }
    else
        err "npm não disponível para fallback do OpenCode CLI."
        return 1
    fi
}

# ---------------------------------------------------------------------------
install_antigravity_cli() {
    log "Instalando Antigravity CLI (agy)..."
    if command -v agy >/dev/null 2>&1 || [ -x "$HOME/.local/bin/agy" ]; then
        ok "Antigravity CLI já instalado."
        return 0
    fi
    curl -fsSL https://antigravity.google/cli/install.sh | bash >>"$LOG_FILE" 2>&1
    export PATH="$HOME/.local/bin:$PATH"
    if command -v agy >/dev/null 2>&1 || [ -x "$HOME/.local/bin/agy" ]; then
        ok "Antigravity CLI instalado em ~/.local/bin/agy"
        return 0
    fi
    err "Falha ao instalar Antigravity CLI (verifique conectividade/log)."
    return 1
}

# ---------------------------------------------------------------------------
install_claude_code_cli() {
    log "Instalando Claude Code CLI (@anthropic-ai/claude-code)..."
    if command -v claude >/dev/null 2>&1; then
        ok "Claude Code CLI já instalado: $(claude --version 2>/dev/null | head -1)"
        return 0
    fi
    if ! command -v npm >/dev/null 2>&1; then
        warn "npm não encontrado — instale o Node.js antes do Claude Code CLI."
        return 1
    fi
    (command -v sudo >/dev/null 2>&1 && sudo npm install -g @anthropic-ai/claude-code || npm install -g @anthropic-ai/claude-code) >>"$LOG_FILE" 2>&1
    if command -v claude >/dev/null 2>&1; then
        ok "Claude Code CLI instalado: $(claude --version 2>/dev/null | head -1)"
        return 0
    fi
    err "Falha ao instalar Claude Code CLI (verifique o log). Autentique depois com: claude"
    return 1
}

# ---------------------------------------------------------------------------
install_ollama_cli() {
    log "Instalando Ollama CLI..."
    if command -v ollama >/dev/null 2>&1; then
        ok "Ollama já instalado: $(ollama --version 2>/dev/null | head -1)"
    else
        curl -fsSL https://ollama.com/install.sh | sh >>"$LOG_FILE" 2>&1
        if command -v ollama >/dev/null 2>&1; then
            ok "Ollama instalado: $(ollama --version 2>/dev/null | head -1)"
        else
            warn "Instalador oficial do Ollama falhou; tentando fallback via binário estático..."
            local ollama_bin="$HOME/.local/bin/ollama"
            mkdir -p "$HOME/.local/bin"
            local ollama_url="https://github.com/ollama/ollama/releases/latest/download/ollama-linux-amd64"
            curl -fsSL "$ollama_url" -o "$ollama_bin" >>"$LOG_FILE" 2>&1 && \
                chmod +x "$ollama_bin" && \
                ok "Ollama instalado via binário estático." || \
                { err "Falha ao instalar Ollama (verifique o log)."; return 1; }
        fi
    fi

    export PATH="$HOME/.local/bin:$PATH"
    if command -v systemctl >/dev/null 2>&1 && systemctl is-system-running >/dev/null 2>&1; then
        (command -v sudo >/dev/null 2>&1 && sudo systemctl enable --now ollama || systemctl enable --now ollama) >>"$LOG_FILE" 2>&1 || true
    fi
    if ! pgrep -f "ollama serve" >/dev/null 2>&1 && \
       ! (command -v systemctl >/dev/null 2>&1 && systemctl is-active --quiet ollama 2>/dev/null); then
        nohup ollama serve >>"$LOG_FILE" 2>&1 &
        sleep 2
    fi
    ok "Serviço Ollama ativo (ou iniciado em segundo plano)."
}

# ---------------------------------------------------------------------------
# Instala as 4 CLIs em sequência. Retorna 0 mesmo se alguma falhar
# (best-effort) — cada instalador registra seu próprio status.
# ---------------------------------------------------------------------------
install_all_clis() {
    install_opencode_cli
    install_antigravity_cli
    install_claude_code_cli
    install_ollama_cli
    return 0
}
