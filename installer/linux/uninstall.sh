#!/usr/bin/env bash
# ============================================================================
# OpenCode Ecosystem Core — Desinstalador Linux nativo
# ----------------------------------------------------------------------------
# Por padrão remove APENAS o que é seguro reverter: o launcher .desktop e
# os aliases adicionados ao .bashrc/.zshrc. NÃO remove, por padrão, o
# repositório clonado nem as CLIs externas (opencode/agy/claude/ollama) —
# essas são ações destrutivas/compartilhadas e exigem flags + confirmação.
#
# Uso:
#   bash installer/linux/uninstall.sh                         # remove so o launcher/aliases (seguro)
#   bash installer/linux/uninstall.sh --remove-repo            # tambem apaga o repositorio clonado
#   bash installer/linux/uninstall.sh --remove-clis             # tambem desinstala opencode/agy/claude/ollama
#   bash installer/linux/uninstall.sh --remove-repo --remove-clis --yes   # sem confirmacao interativa
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
err()  { echo -e "${C_RED}[ERRO]${C_OFF} $*"; }

confirm() {
    # confirm "pergunta" -> 0 (sim) ou 1 (nao)
    if [ "$ASSUME_YES" = true ]; then return 0; fi
    read -r -p "$1 Digite CONFIRMO para prosseguir: " answer
    [ "$answer" = "CONFIRMO" ]
}

echo "==================================================================="
echo "  OpenCode Ecosystem Core — Desinstalador Linux"
echo "==================================================================="

# ---------------------------------------------------------------------------
# 1. Remover launcher .desktop
# ---------------------------------------------------------------------------
log "Etapa 1/3: Removendo launcher (.desktop)..."
rm -f "$HOME/.local/share/applications/opencode-ecosystem.desktop" && ok "Launcher removido de ~/.local/share/applications/"
for candidate in "$HOME/Desktop" "$HOME/Área de Trabalho" "$HOME/Escritorio"; do
    if [ -f "$candidate/opencode-ecosystem.desktop" ]; then
        rm -f "$candidate/opencode-ecosystem.desktop"
        ok "Launcher removido de $candidate"
    fi
done

# ---------------------------------------------------------------------------
# 2. Remover aliases do shell
# ---------------------------------------------------------------------------
log "Etapa 2/3: Removendo aliases do shell..."
for rc in "$HOME/.bashrc" "$HOME/.zshrc"; do
    [ -f "$rc" ] || continue
    sed -i.bak \
        -e "\|alias ecosystem=|d" \
        -e "\|alias eco-opencode=|d" \
        -e "\|alias eco-agy=|d" \
        -e "\|alias eco-claude=|d" \
        "$rc" 2>/dev/null && ok "Aliases removidos de $rc (backup em $rc.bak)"
done

# ---------------------------------------------------------------------------
# 3. Ações destrutivas (opt-in, com confirmação)
# ---------------------------------------------------------------------------
log "Etapa 3/3: Ações destrutivas (opcionais)"

if [ "$REMOVE_CLIS" = true ]; then
    if confirm "Isso vai DESINSTALAR opencode/agy/claude/ollama do sistema (podem ser usados por outros projetos)."; then
        npm uninstall -g opencode-ai @anthropic-ai/claude-code >/dev/null 2>&1 || true
        rm -f "$HOME/.local/bin/agy" "$HOME/.local/bin/ollama" 2>/dev/null || true
        rm -rf "$HOME/.opencode" 2>/dev/null || true
        ok "CLIs removidas (best-effort — alguns binários podem ter sido instalados de outra forma)."
    else
        warn "Remoção das CLIs cancelada pelo usuário."
    fi
else
    echo "CLIs externas NÃO removidas (use --remove-clis)."
fi

if [ "$REMOVE_REPO" = true ]; then
    if confirm "Isso vai APAGAR PERMANENTEMENTE $ECO_DIR, incluindo qualquer trabalho não salvo em outro lugar."; then
        rm -rf "$ECO_DIR"
        ok "Repositório removido: $ECO_DIR"
    else
        warn "Remoção do repositório cancelada pelo usuário."
    fi
else
    echo "Repositório clonado NÃO removido (use --remove-repo). Local: $ECO_DIR"
fi

echo ""
ok "Desinstalação concluída."
