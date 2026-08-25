#!/bin/bash
# ============================================================================
# OpenCode Ecosystem Core — Instalador nativo para Linux (sem WSL)
# ----------------------------------------------------------------------------
# Uso seguro: clone o repositório, confira uma revisão imutável e execute este
# arquivo localmente. Este instalador não aceita execução por pipe de rede.
#
# Caminho principal testado: distros baseadas em Debian/Ubuntu (apt-get).
# Outras distros (Fedora/Arch/openSUSE) recebem um aviso claro e a
# instalação prossegue best-effort (dependências de sistema podem faltar).
# Idempotente: pode ser reexecutado com segurança para atualizar tudo.
# ============================================================================
set -uo pipefail

INSTALLER_SAFE_PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
export PATH="$INSTALLER_SAFE_PATH"

REPO_URL="${ECOSYSTEM_REPO_URL:-https://github.com/MarceloClaro/opencode-ecosystem-core.git}"
ECO_DIR="${ECOSYSTEM_DIR:-$HOME/opencode-ecosystem-core}"
ECOSYSTEM_REF="${ECOSYSTEM_REF:-}"
LOG_FILE="$HOME/.opencode-ecosystem-install.log"

C_GREEN='\033[0;32m'; C_YELLOW='\033[1;33m'; C_RED='\033[0;31m'; C_CYAN='\033[0;36m'; C_OFF='\033[0m'
log()  { echo -e "${C_CYAN}[ECOSYSTEM]${C_OFF} $*" | tee -a "$LOG_FILE"; }
ok()   { echo -e "${C_GREEN}[OK]${C_OFF} $*"       | tee -a "$LOG_FILE"; }
warn() { echo -e "${C_YELLOW}[AVISO]${C_OFF} $*"   | tee -a "$LOG_FILE"; }
err()  { echo -e "${C_RED}[ERRO]${C_OFF} $*"       | tee -a "$LOG_FILE"; }

SCRIPT_DIR="$(cd -- "$(dirname "${BASH_SOURCE[0]}")" && pwd)" || { err "Não foi possível localizar o instalador."; exit 1; }
SCRIPT_ROOT="$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd -P)" || { err "Não foi possível localizar a raiz do checkout do instalador."; exit 1; }
PATH_SAFETY_LIB="$SCRIPT_ROOT/installer/common/path_safety.sh"

checkout_worktree_is_clean() {
    local checkout="$1"

    [[ -z "$(git -c safe.directory="$checkout" -C "$checkout" status --porcelain=v1 --untracked-files=all --ignore-submodules=none 2>/dev/null)" ]]
}

repository_url_is_secure() {
    local url="$1" authority

    [[ "$url" =~ ^https:// ]] || return 1
    [[ "$url" != *$'\n'* && "$url" != *$'\r'* && "$url" != *$'\t'* && "$url" != *' '* ]] || return 1
    [[ "$url" != *"?"* && "$url" != *"#"* ]] || return 1
    authority="${url#https://}"
    authority="${authority%%/*}"
    [[ -n "$authority" && "$authority" != *"@"* ]]
}

preflight_immutable_checkout() {
    # Este preflight ocorre antes de qualquer elevação, gerenciador de pacotes
    # ou instalação de CLI. Ele não atualiza nem corrige checkouts existentes.
    local source_dir source_top source_head target_dir target_top target_head requested_ref

    if ! repository_url_is_secure "$REPO_URL"; then
        err "ECOSYSTEM_REPO_URL deve ser HTTPS, sem credenciais, consulta, fragmento ou espaços."
        return 1
    fi
    if [[ ! "$ECOSYSTEM_REF" =~ ^[0-9a-fA-F]{40}$ ]]; then
        err "Defina ECOSYSTEM_REF com o hash completo de commit Git a instalar."
        return 1
    fi
    if ! command -v git >/dev/null 2>&1; then
        err "git é necessário para validar o checkout local antes da instalação."
        return 1
    fi

    source_dir="$SCRIPT_ROOT"
    if [[ -n "${ECOSYSTEM_SOURCE_DIR:-}" ]]; then
        source_dir="$(CDPATH= cd -- "$ECOSYSTEM_SOURCE_DIR" && pwd -P)" || {
            err "Não foi possível canonicalizar ECOSYSTEM_SOURCE_DIR."
            return 1
        }
        if [[ "$source_dir" != "$SCRIPT_ROOT" ]]; then
            err "ECOSYSTEM_SOURCE_DIR não pode divergir da árvore que fornece este instalador Linux."
            return 1
        fi
    fi
    if [[ ! -d "$source_dir" ]]; then
        err "O checkout-fonte local não existe: $source_dir"
        return 1
    fi
    if [[ "$(git -c safe.directory="$source_dir" -C "$source_dir" rev-parse --is-inside-work-tree 2>/dev/null || true)" != "true" ]]; then
        err "O checkout-fonte local não é um repositório Git utilizável."
        return 1
    fi
    source_top="$(git -c safe.directory="$source_dir" -C "$source_dir" rev-parse --show-toplevel 2>/dev/null)" || {
        err "Não foi possível identificar a raiz do checkout-fonte local."
        return 1
    }
    source_top="$(CDPATH= cd -- "$source_top" && pwd -P)" || return 1
    if [[ "$source_top" != "$source_dir" ]]; then
        err "O checkout-fonte deve apontar para a raiz do repositório Git local."
        return 1
    fi
    if ! checkout_worktree_is_clean "$source_dir"; then
        err "O checkout-fonte local possui alterações ou arquivos não rastreados; nada será instalado."
        return 1
    fi
    source_head="$(git -c safe.directory="$source_dir" -C "$source_dir" rev-parse --verify 'HEAD^{commit}' 2>/dev/null)" || {
        err "O checkout-fonte local não possui HEAD de commit verificável."
        return 1
    }
    requested_ref="$(printf '%s' "$ECOSYSTEM_REF" | tr '[:upper:]' '[:lower:]')"
    if [[ "$(printf '%s' "$source_head" | tr '[:upper:]' '[:lower:]')" != "$requested_ref" ]]; then
        err "HEAD do checkout-fonte ($source_head) difere de ECOSYSTEM_REF; nada será instalado."
        return 1
    fi

    if [[ -e "$ECO_DIR" || -L "$ECO_DIR" ]]; then
        if [[ -L "$ECO_DIR" || ! -d "$ECO_DIR" ]]; then
            err "$ECO_DIR existe, mas não é um diretório real de checkout Git."
            return 1
        fi
        target_dir="$(CDPATH= cd -- "$ECO_DIR" && pwd -P)" || {
            err "Não foi possível canonicalizar o destino existente."
            return 1
        }
        if [[ "$(git -C "$target_dir" rev-parse --is-inside-work-tree 2>/dev/null || true)" != "true" ]]; then
            err "$ECO_DIR existe e não é um checkout Git; não será alterado."
            return 1
        fi
        target_top="$(git -C "$target_dir" rev-parse --show-toplevel 2>/dev/null)" || {
            err "Não foi possível identificar a raiz do checkout de destino."
            return 1
        }
        target_top="$(CDPATH= cd -- "$target_top" && pwd -P)" || return 1
        if [[ "$target_top" != "$target_dir" ]]; then
            err "$ECO_DIR deve ser a raiz do checkout Git existente."
            return 1
        fi
        if ! checkout_worktree_is_clean "$target_dir"; then
            err "O checkout de destino possui alterações ou arquivos não rastreados; não será alterado."
            return 1
        fi
        target_head="$(git -C "$target_dir" rev-parse --verify 'HEAD^{commit}' 2>/dev/null)" || {
            err "O checkout de destino não possui HEAD de commit verificável."
            return 1
        }
        if [[ "$(printf '%s' "$target_head" | tr '[:upper:]' '[:lower:]')" != "$requested_ref" ]]; then
            err "Checkout de destino ($target_head) difere de ECOSYSTEM_REF; não será alterado."
            return 1
        fi
    fi
    return 0
}

if ! preflight_immutable_checkout; then
    err "Preflight de checkout imutável falhou antes de operações privilegiadas."
    exit 1
fi
if [ ! -f "$PATH_SAFETY_LIB" ]; then
    err "Biblioteca local path_safety.sh ausente no checkout já validado."
    exit 1
fi
# shellcheck source=/dev/null
source "$PATH_SAFETY_LIB"

if ! validate_ecosystem_dir "$ECO_DIR"; then
    err "ECOSYSTEM_DIR recusado antes de qualquer instalação ou persistência."
    exit 1
fi
if ! validate_ecosystem_dir_no_symlink_prefix "$ECO_DIR"; then
    err "ECOSYSTEM_DIR possui pai simbólico ou inválido antes do clone."
    exit 1
fi
COMMON_LIB="$SCRIPT_ROOT/installer/common/install_clis.sh"
if [ ! -f "$COMMON_LIB" ]; then
    err "install_clis.sh local ausente. Execute a partir de um checkout completo e validado."
    exit 1
fi
# shellcheck source=/dev/null
source "$COMMON_LIB"
if ! preflight_external_artifacts; then
    err "Metadados de artefatos externos inválidos; nenhuma operação privilegiada será iniciada."
    exit 1
fi

echo "==================================================================="
echo "  OpenCode Ecosystem Core — Instalador Linux Nativo"
echo "  Log: $LOG_FILE"
echo "==================================================================="

if ! sudo -v; then
    err "Não foi possível autenticar sudo. Nenhuma permissão persistente será criada."
    exit 1
fi
trap 'sudo -k >/dev/null 2>&1 || true' EXIT

# ---------------------------------------------------------------------------
# 1. Dependências do sistema
# ---------------------------------------------------------------------------
log "Etapa 1/4: Instalando dependências do sistema..."
if command -v apt-get >/dev/null 2>&1; then
    sudo apt-get update -y >>"$LOG_FILE" 2>&1 || { err "Falha ao atualizar índices apt."; exit 1; }
    sudo DEBIAN_FRONTEND=noninteractive apt-get install -y \
        git curl wget unzip zip ca-certificates \
        python3 python3-pip python3-venv \
        pandoc poppler-utils build-essential zstd \
        nodejs npm >>"$LOG_FILE" 2>&1 || { err "Falha ao instalar dependências apt."; exit 1; }
    ok "Dependências do sistema instaladas (apt)."
elif command -v dnf >/dev/null 2>&1; then
    warn "Distro baseada em Fedora/RHEL detectada — caminho best-effort (menos testado que Debian/Ubuntu)."
    sudo dnf install -y git curl wget unzip zip python3 python3-pip pandoc poppler-utils \
        gcc gcc-c++ make nodejs npm zstd >>"$LOG_FILE" 2>&1 || { err "Falha ao instalar dependências dnf."; exit 1; }
    ok "Dependências do sistema instaladas (dnf)."
elif command -v pacman >/dev/null 2>&1; then
    warn "Distro baseada em Arch detectada — caminho best-effort (menos testado que Debian/Ubuntu)."
    sudo pacman -Sy --noconfirm git curl wget unzip zip python python-pip pandoc poppler \
        base-devel nodejs npm zstd >>"$LOG_FILE" 2>&1 || { err "Falha ao instalar dependências pacman."; exit 1; }
    ok "Dependências do sistema instaladas (pacman)."
else
    err "Gerenciador de pacotes não reconhecido (apt/dnf/pacman); não é seguro prosseguir sem dependências verificadas."
    exit 1
fi

# O ticket obtido apenas para dependências não pode ser reutilizado pelas CLIs.
sudo -k >/dev/null 2>&1 || { err "Não foi possível invalidar o ticket sudo após as dependências."; exit 1; }

# ---------------------------------------------------------------------------
# 2. CLIs externas (OpenCode, Antigravity, Claude Code, Ollama)
# ---------------------------------------------------------------------------
log "Etapa 2/4: Instalando CLIs externas..."
if ! install_all_clis; then
    err "CLIs ausentes ou sem artefatos verificados; instalação interrompida."
    exit 1
fi

# ---------------------------------------------------------------------------
# 3. OpenCode Ecosystem Core
# ---------------------------------------------------------------------------
log "Etapa 3/4: Instalando o OpenCode Ecosystem Core..."
if [[ -e "$ECO_DIR" || -L "$ECO_DIR" ]]; then
    if [[ -L "$ECO_DIR" || ! -d "$ECO_DIR" ]]; then
        err "$ECO_DIR existe e não é um checkout Git; não será removido automaticamente."
        exit 1
    fi
    installed_ref="$(git -C "$ECO_DIR" rev-parse --verify 'HEAD^{commit}' 2>/dev/null || true)"
    if [[ "$(printf '%s' "$installed_ref" | tr '[:upper:]' '[:lower:]')" != "$(printf '%s' "$ECOSYSTEM_REF" | tr '[:upper:]' '[:lower:]')" ]]; then
        err "Checkout existente ($installed_ref) difere de ECOSYSTEM_REF; não será alterado automaticamente."
        exit 1
    fi
    ok "Checkout local já corresponde à revisão imutável solicitada."
else
    git clone "$REPO_URL" "$ECO_DIR" >>"$LOG_FILE" 2>&1 || { err "Falha ao clonar $REPO_URL."; exit 1; }
    git -C "$ECO_DIR" checkout --detach "$ECOSYSTEM_REF" >>"$LOG_FILE" 2>&1 || { err "Revisão solicitada não encontrada."; exit 1; }
    installed_ref="$(git -C "$ECO_DIR" rev-parse HEAD)"
    if [[ "$(printf '%s' "$installed_ref" | tr '[:upper:]' '[:lower:]')" != "$(printf '%s' "$ECOSYSTEM_REF" | tr '[:upper:]' '[:lower:]')" ]]; then
        err "Hash do checkout não confere com ECOSYSTEM_REF."
        exit 1
    fi
    ok "Ecosystem clonado e validado em $installed_ref."
fi

ECO_DIR="$(canonicalize_ecosystem_dir "$ECO_DIR")" || {
    err "ECOSYSTEM_DIR não pôde ser canonicalizado dentro de HOME."
    exit 1
}

VENV_PYTHON="$ECO_DIR/.venv/bin/python"
if [ ! -f "$ECO_DIR/requirements.txt" ]; then
    err "requirements.txt ausente; não é seguro usar o interpretador global."
    exit 1
fi
python3 -m venv "$ECO_DIR/.venv" >>"$LOG_FILE" 2>&1 || { err "Falha ao criar ambiente virtual."; exit 1; }
[ -x "$VENV_PYTHON" ] || { err "Interpretador da virtualenv não foi criado."; exit 1; }
"$VENV_PYTHON" -m pip install --require-virtualenv -q -r "$ECO_DIR/requirements.txt" >>"$LOG_FILE" 2>&1 \
   || { err "Falha ao instalar requirements pinados."; exit 1; }
ok "Dependências Python pinadas instaladas em .venv."

if [ -f "$ECO_DIR/assets/generate_icon.py" ]; then
    (cd -- "$ECO_DIR" && "$VENV_PYTHON" assets/generate_icon.py >>"$LOG_FILE" 2>&1) && ok "Ícone gerado." || warn "Falha ao gerar ícone (Pillow ausente?)."
fi

# ---------------------------------------------------------------------------
# 4. Integração e smoke tests (antes de aliases e atalhos persistentes)
# ---------------------------------------------------------------------------
log "Etapa 4/4: Configurando integração e validando a instalação..."
if [ -f "$ECO_DIR/integrations/opencode_cli.py" ]; then
    (cd -- "$ECO_DIR" && "$VENV_PYTHON" -c "
from integrations.opencode_cli import OpenCodeCLIIntegration
integ = OpenCodeCLIIntegration('.')
path = integ.generate_config()
print(f'opencode.json regenerado: {path}')
" >>"$LOG_FILE" 2>&1) || { err "Não foi possível regenerar opencode.json."; exit 1; }
    ok "Integração nativa OpenCode CLI configurada."
fi

echo ""
echo "==================================================================="
echo "  VERIFICAÇÃO FINAL"
echo "==================================================================="
export PATH="$HOME/.opencode/bin:$HOME/.local/bin:$PATH"
FAIL=0
for tool in opencode agy claude ollama git pandoc; do
    if command -v "$tool" >/dev/null 2>&1; then
        ok "$tool disponível."
    else
        err "$tool NÃO encontrado."
        FAIL=1
    fi
done

if [ -x "$VENV_PYTHON" ]; then
    ok "Interpretador da virtualenv disponível."
else
    err "Interpretador da virtualenv não encontrado."
    FAIL=1
fi
if [ -d "$ECO_DIR" ] && (cd -- "$ECO_DIR" && "$VENV_PYTHON" -c "from marceloclaro.orchestrator import MarceloClaroOrchestrator" 2>>"$LOG_FILE"); then
    ok "Ecossistema importável (orquestrador marceloclaro OK)."
else
    err "Ecossistema não importável — verifique $LOG_FILE."
    FAIL=1
fi
if [ -d "$ECO_DIR" ] && (cd -- "$ECO_DIR" && "$VENV_PYTHON" -m marceloclaro.cli doctor >>"$LOG_FILE" 2>&1); then
    ok "Doctor executado pela virtualenv."
else
    err "Doctor falhou — verifique $LOG_FILE."
    FAIL=1
fi

if [ "$FAIL" -ne 0 ]; then
    err "Smoke tests falharam; integração e atalhos não serão criados."
    exit 1
fi

SHELL_RC="$HOME/.bashrc"
[ -n "${ZSH_VERSION:-}" ] && SHELL_RC="$HOME/.zshrc"
if ! validate_ecosystem_dir "$ECO_DIR"; then
    err "ECOSYSTEM_DIR recusado antes de gravar aliases ou launchers."
    exit 1
fi
add_line() { grep -qxF "$1" "$SHELL_RC" 2>/dev/null || printf '%s\n' "$1" >> "$SHELL_RC"; }
add_line 'export PATH="$HOME/.opencode/bin:$HOME/.local/bin:$PATH"' || { err "Falha ao atualizar $SHELL_RC."; exit 1; }
add_line "alias ecosystem='cd -- \"$ECO_DIR\" && \"$VENV_PYTHON\" -m marceloclaro.cli'" || { err "Falha ao criar alias ecosystem."; exit 1; }
add_line "alias eco-opencode='cd -- \"$ECO_DIR\" && opencode'" || { err "Falha ao criar alias eco-opencode."; exit 1; }
add_line "alias eco-agy='cd -- \"$ECO_DIR\" && agy'" || { err "Falha ao criar alias eco-agy."; exit 1; }
add_line "alias eco-claude='cd -- \"$ECO_DIR\" && claude'" || { err "Falha ao criar alias eco-claude."; exit 1; }

# Launcher .desktop (padrão freedesktop.org — funciona em GNOME/KDE/XFCE...)
DESKTOP_FILE_DIR="$HOME/.local/share/applications"
mkdir -p "$DESKTOP_FILE_DIR" || { err "Não foi possível criar o diretório de atalhos."; exit 1; }
desktop_temporary="$(mktemp "$DESKTOP_FILE_DIR/.opencode-ecosystem.desktop.XXXXXX")" || { err "Não foi possível preparar o launcher."; exit 1; }
ICON_PATH="$ECO_DIR/assets/icon.png"
if ! cat > "$desktop_temporary" <<EOF
[Desktop Entry]
Type=Application
Name=Ecosystem (marceloclaro)
Comment=CLI interativo do orquestrador metacognitivo marceloclaro
Exec=x-terminal-emulator -e /bin/bash -lic "cd -- \"$ECO_DIR\" && \"$VENV_PYTHON\" -m marceloclaro.cli"
Icon=$ICON_PATH
Terminal=true
Categories=Development;
EOF
then
    rm -f "$desktop_temporary"
    err "Falha ao gravar launcher temporário."
    exit 1
fi
chmod +x "$desktop_temporary" && mv -f "$desktop_temporary" "$DESKTOP_FILE_DIR/opencode-ecosystem.desktop" \
    || { rm -f "$desktop_temporary"; err "Falha ao criar launcher."; exit 1; }
ok "Launcher criado em $DESKTOP_FILE_DIR/opencode-ecosystem.desktop"

# Copia também para a Área de Trabalho, se existir.
for candidate in "$HOME/Desktop" "$HOME/Área de Trabalho" "$HOME/Escritorio"; do
    if [ -d "$candidate" ]; then
        if cp "$DESKTOP_FILE_DIR/opencode-ecosystem.desktop" "$candidate/" 2>/dev/null && chmod +x "$candidate/opencode-ecosystem.desktop" 2>/dev/null; then
            ok "Atalho copiado para $candidate"
        else
            warn "Não foi possível copiar o atalho para $candidate."
        fi
        break
    fi
done

echo ""
ok "Instalação concluída com sucesso! Abra um novo terminal e rode: ecosystem"
echo "Para desinstalar: bash $ECO_DIR/installer/linux/uninstall.sh"
exit 0
