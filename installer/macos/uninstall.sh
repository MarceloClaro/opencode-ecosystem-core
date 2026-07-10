#!/usr/bin/env bash
# ============================================================================
# OpenCode Ecosystem Core — Desinstalador macOS (best-effort)
# ----------------------------------------------------------------------------
# Uso:
#   bash installer/macos/uninstall.sh                          # remove so o launcher/aliases (seguro)
#   bash installer/macos/uninstall.sh --remove-repo             # tambem apaga o repositorio clonado
#   bash installer/macos/uninstall.sh --remove-clis              # tambem desinstala opencode/agy/claude/ollama
#   bash installer/macos/uninstall.sh --remove-repo --remove-clis --yes
# ============================================================================
set -uo pipefail

ECO_DIR="${ECOSYSTEM_DIR:-$HOME/opencode-ecosystem-core}"

REMOVE_REPO=false
REMOVE_CLIS=false
ASSUME_YES=false
for arg in "$@"; do
    case "$arg" in
        --remove-repo) REMOVE_REPO=true ;;
        --remove-clis) REMOVE_CLIS=true ;;
        --yes|-y) ASSUME_YES=true ;;
        *) echo "Argumento desconhecido: $arg" ;;
    esac
done

C_GREEN='\033[0;32m'; C_YELLOW='\033[1;33m'; C_RED='\033[0;31m'; C_CYAN='\033[0;36m'; C_OFF='\033[0m'
log()  { echo -e "${C_CYAN}[ECOSYSTEM]${C_OFF} $*"; }
ok()   { echo -e "${C_GREEN}[OK]${C_OFF} $*"; }
warn() { echo -e "${C_YELLOW}[AVISO]${C_OFF} $*"; }

confirm() {
    if [ "$ASSUME_YES" = true ]; then return 0; fi
    read -r -p "$1 Digite CONFIRMO para prosseguir: " answer
    [ "$answer" = "CONFIRMO" ]
}

echo "==================================================================="
echo "  OpenCode Ecosystem Core — Desinstalador macOS (best-effort)"
echo "==================================================================="

log "Etapa 1/3: Removendo launcher (.command) da Área de Trabalho..."
rm -f "$HOME/Desktop/Ecosystem (marceloclaro).command" && ok "Launcher removido."

log "Etapa 2/3: Removendo aliases do shell..."
for rc in "$HOME/.zshrc" "$HOME/.bash_profile"; do
    [ -f "$rc" ] || continue
    sed -i.bak -e "\|alias ecosystem=|d" "$rc" 2>/dev/null && ok "Aliases removidos de $rc (backup em $rc.bak)"
done

log "Etapa 3/3: Ações destrutivas (opcionais)"
if [ "$REMOVE_CLIS" = true ]; then
    if confirm "Isso vai DESINSTALAR opencode/agy/claude/ollama (podem ser usados por outros projetos)."; then
        npm uninstall -g opencode-ai @anthropic-ai/claude-code >/dev/null 2>&1 || true
        rm -f "$HOME/.local/bin/agy" 2>/dev/null || true
        command -v brew >/dev/null 2>&1 && brew uninstall ollama >/dev/null 2>&1 || true
        ok "CLIs removidas (best-effort)."
    else
        warn "Remoção das CLIs cancelada pelo usuário."
    fi
else
    echo "CLIs externas NÃO removidas (use --remove-clis)."
fi

if [ "$REMOVE_REPO" = true ]; then
    if confirm "Isso vai APAGAR PERMANENTEMENTE $ECO_DIR."; then
        rm -rf "$ECO_DIR"
        ok "Repositório removido: $ECO_DIR"
    else
        warn "Remoção do repositório cancelada pelo usuário."
    fi
else
    echo "Repositório clonado NÃO removido (use --remove-repo). Local: $ECO_DIR"
fi

echo ""
ok "Desinstalação concluída (best-effort)."
