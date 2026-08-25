#!/bin/bash
# ============================================================================
# OpenCode Ecosystem Core — Provisioner WSL/Ubuntu
# ----------------------------------------------------------------------------
# Executado DENTRO do Ubuntu (WSL) pelo bootstrap PowerShell, ou manualmente:
#   bash provision.sh
#
# Instala: OpenCode CLI, Antigravity CLI, Claude Code CLI, Ollama CLI,
# dependências do sistema e o repositório opencode-ecosystem-core
# (nativo no OpenCode CLI).
# A instalação automática exige artefatos e revisão imutáveis informados pelo
# operador. Não execute este arquivo por pipe de rede.
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

SCRIPT_DIR="$(cd -- "$(dirname "${BASH_SOURCE[0]}")" && pwd)" || { err "Não foi possível localizar o provisionador."; exit 1; }
SCRIPT_ROOT="$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd -P)" || { err "Não foi possível localizar a raiz da árvore do provisionador."; exit 1; }
if [[ ! -e "$SCRIPT_ROOT/.git" ]]; then
    SCRIPT_ROOT="$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd -P)" || { err "Não foi possível localizar a raiz do staging WSL."; exit 1; }
fi
PATH_SAFETY_LIB="$SCRIPT_DIR/../common/path_safety.sh"

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

staged_sha256_file() {
    local path="$1"

    if command -v sha256sum >/dev/null 2>&1; then
        sha256sum "$path" | cut -d ' ' -f1
    elif command -v shasum >/dev/null 2>&1; then
        shasum -a 256 "$path" | cut -d ' ' -f1
    else
        err "Nenhuma ferramenta SHA-256 disponível para atestar o provisionador em staging."
        return 1
    fi
}

verify_staged_installer_attestation() {
    # O staging WSL não é um checkout Git. Quando ele é separado do checkout
    # fonte, só pode fornecer código após os três bytes terem sido atestados.
    local provision_path="$SCRIPT_DIR/provision.sh"
    local common_path="$SCRIPT_DIR/../common/install_clis.sh"
    local path_safety_path="$PATH_SAFETY_LIB"
    local expected_provision="${ECOSYSTEM_PROVISION_SHA256:-}"
    local expected_common="${ECOSYSTEM_COMMON_INSTALLER_SHA256:-}"
    local expected_path_safety="${ECOSYSTEM_PATH_SAFETY_SHA256:-}"
    local actual expected path

    if [[ "${ECOSYSTEM_STAGED_INSTALLER:-}" != "1" ]]; then
        err "ECOSYSTEM_SOURCE_DIR externo exige atestação explícita do staging WSL."
        return 1
    fi
    for expected in "$expected_provision" "$expected_common" "$expected_path_safety"; do
        if [[ ! "$expected" =~ ^[A-Fa-f0-9]{64}$ ]]; then
            err "A atestação do staging WSL exige três SHA-256 explícitos de 64 dígitos."
            return 1
        fi
    done
    for path in "$provision_path" "$common_path" "$path_safety_path"; do
        if [[ ! -f "$path" || -L "$path" ]]; then
            err "Arquivo de staging WSL ausente ou simbólico; não será carregado."
            return 1
        fi
    done
    actual="$(staged_sha256_file "$provision_path")" || return 1
    if [[ "${actual,,}" != "${expected_provision,,}" ]]; then
        err "A atestação de provision.sh em staging diverge; nada será instalado."
        return 1
    fi
    actual="$(staged_sha256_file "$common_path")" || return 1
    if [[ "${actual,,}" != "${expected_common,,}" ]]; then
        err "A atestação de install_clis.sh em staging diverge; nada será instalado."
        return 1
    fi
    actual="$(staged_sha256_file "$path_safety_path")" || return 1
    if [[ "${actual,,}" != "${expected_path_safety,,}" ]]; then
        err "A atestação de path_safety.sh em staging diverge; nada será instalado."
        return 1
    fi
}

preflight_immutable_checkout() {
    # Este preflight ocorre antes de sudo, apt ou instalação de CLI. Quando o
    # wrapper usa uma cópia de staging, ECOSYSTEM_SOURCE_DIR aponta para o
    # checkout local original que declara a revisão solicitada.
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
        err "git é necessário para validar o checkout local antes do provisionamento."
        return 1
    fi

    source_dir="$SCRIPT_ROOT"
    if [[ -n "${ECOSYSTEM_SOURCE_DIR:-}" ]]; then
        source_dir="$(CDPATH= cd -- "$ECOSYSTEM_SOURCE_DIR" && pwd -P)" || {
            err "Não foi possível canonicalizar ECOSYSTEM_SOURCE_DIR."
            return 1
        }
        if [[ "$source_dir" != "$SCRIPT_ROOT" ]] && ! verify_staged_installer_attestation; then
            return 1
        fi
    fi
    if [[ ! -d "$source_dir" ]]; then
        err "O checkout-fonte local não existe: $source_dir"
        return 1
    fi
    source_dir="$(CDPATH= cd -- "$source_dir" && pwd -P)" || {
        err "Não foi possível canonicalizar o checkout-fonte local."
        return 1
    }
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
    err "Biblioteca local path_safety.sh ausente após o preflight."
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

COMMON_LIB="$SCRIPT_DIR/../common/install_clis.sh"
if [ ! -f "$COMMON_LIB" ]; then
    err "Biblioteca local install_clis.sh ausente. Clone uma revisão imutável do repositório e execute o instalador localmente."
    exit 1
fi
# shellcheck source=/dev/null
source "$COMMON_LIB"
if ! preflight_external_artifacts; then
    err "Metadados de artefatos externos inválidos; nenhuma operação privilegiada será iniciada."
    exit 1
fi

for cli_installer in \
    install_opencode_cli \
    install_antigravity_cli \
    install_claude_code_cli \
    install_ollama_cli; do
    if ! declare -F "$cli_installer" >/dev/null 2>&1; then
        err "Biblioteca de CLIs incompleta: função $cli_installer ausente."
        exit 1
    fi
done

echo "==================================================================="
echo "  OpenCode Ecosystem Core — Provisionamento do Ubuntu (WSL)"
echo "  Log: $LOG_FILE"
echo "==================================================================="

# ---------------------------------------------------------------------------
# 0. Elevação pontual de privilégio
# ---------------------------------------------------------------------------
log "Validando credencial sudo para operações pontuais..."
if ! sudo -v; then
    err "Não foi possível autenticar sudo. Nenhum sudoers persistente será criado."
    exit 1
fi
trap 'sudo -k >/dev/null 2>&1 || true' EXIT

# ---------------------------------------------------------------------------
# 1. Dependências do sistema
#    Inclui zstd (obrigatório desde Ollama v0.4+ para extração do binário)
# ---------------------------------------------------------------------------
log "Etapa 1/4: Atualizando pacotes do sistema (apt)..."
sudo apt-get update -y >>"$LOG_FILE" 2>&1 || { err "Falha ao atualizar índices apt."; exit 1; }
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y \
    git curl wget unzip zip ca-certificates \
    python3 python3-pip python3-venv \
    pandoc poppler-utils \
    build-essential \
    zstd >>"$LOG_FILE" 2>&1 || { err "Falha ao instalar dependências apt."; exit 1; }
ok "Dependências do sistema instaladas (incluindo zstd)."

# Node.js/NPM vêm do repositório da distribuição. Scripts remotos de bootstrap
# não são executados neste instalador.
if ! command -v node >/dev/null 2>&1; then
    sudo apt-get install -y nodejs npm >>"$LOG_FILE" 2>&1 \
        && ok "Node.js/NPM instalados pelo gerenciador da distribuição." \
        || { err "Falha ao instalar Node.js/NPM pela distribuição."; exit 1; }
else
    ok "Node.js/NPM já estão presentes; a versão do binário existente não foi executada."
fi

# O ticket obtido apenas para dependências não pode ser reutilizado pelas CLIs.
sudo -k >/dev/null 2>&1 || { err "Não foi possível invalidar o ticket sudo após as dependências."; exit 1; }

# ---------------------------------------------------------------------------
# 2-4. CLIs externas: OpenCode, Antigravity (agy), Claude Code, Ollama
#      (lógica compartilhada com installer/linux/install.sh e
#      installer/macos/install.sh — ver installer/common/install_clis.sh)
# ---------------------------------------------------------------------------
log "Etapa 2/4: Instalando CLIs externas (OpenCode, Antigravity, Claude Code, Ollama)..."
if ! install_all_clis; then
    err "Uma ou mais CLIs não foram instaladas por artefato verificado; provisionamento interrompido."
    exit 1
fi

# ---------------------------------------------------------------------------
# 5. OpenCode Ecosystem Core (revisão imutável)
# ---------------------------------------------------------------------------
log "Etapa 3/4: Instalando o OpenCode Ecosystem Core em revisão imutável..."
if [[ -e "$ECO_DIR" || -L "$ECO_DIR" ]]; then
    if [[ -L "$ECO_DIR" || ! -d "$ECO_DIR" ]]; then
        err "$ECO_DIR existe e não é um checkout Git; não será removido automaticamente."
        exit 1
    fi
    installed_ref="$(git -C "$ECO_DIR" rev-parse --verify 'HEAD^{commit}' 2>/dev/null || true)"
    if [[ "$(printf '%s' "$installed_ref" | tr '[:upper:]' '[:lower:]')" != "$(printf '%s' "$ECOSYSTEM_REF" | tr '[:upper:]' '[:lower:]')" ]]; then
        err "$ECO_DIR está em $installed_ref, diferente de ECOSYSTEM_REF; não será sobrescrito."
        exit 1
    fi
    ok "Checkout local já corresponde à revisão imutável solicitada."
else
    log "Clonando e validando a revisão solicitada..."
    git clone "$REPO_URL" "$ECO_DIR" >>"$LOG_FILE" 2>&1 || { err "Falha ao clonar $REPO_URL."; exit 1; }
    git -C "$ECO_DIR" checkout --detach "$ECOSYSTEM_REF" >>"$LOG_FILE" 2>&1 || { err "A revisão solicitada não foi encontrada."; exit 1; }
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
python3 -m venv "$ECO_DIR/.venv" >>"$LOG_FILE" 2>&1 || { err "Falha ao criar ambiente virtual Python."; exit 1; }
[ -x "$VENV_PYTHON" ] || { err "Interpretador da virtualenv não foi criado."; exit 1; }
"$VENV_PYTHON" -m pip install --require-virtualenv -q -r "$ECO_DIR/requirements.txt" >>"$LOG_FILE" 2>&1 \
   || { err "Falha ao instalar requirements pinados no ambiente virtual."; exit 1; }
ok "Dependências Python pinadas instaladas em .venv."

# Compilação do motor Colibri MoE em C (nativamente)
if [ -d "$ECO_DIR/colibri/c" ]; then
    log "Compilando motor C do Colibri MoE (olmoe)..."
    (cd -- "$ECO_DIR/colibri/c" && (make >>"$LOG_FILE" 2>&1 || gcc -O3 -o olmoe main.c -lm >>"$LOG_FILE" 2>&1)) \
        || { err "Falha ao compilar binário Colibri C."; exit 1; }
    ok "Binário Colibri MoE (olmoe) compilado com sucesso."
fi

# ---------------------------------------------------------------------------
# 6. Integração nativa e validações antes de aliases/atalhos persistentes
# ---------------------------------------------------------------------------
log "Etapa 4/4: Configurando integração e validando o provisionamento..."

# Instalação opcional do Lean 4 Elan somente por script previamente verificado.
if ! command -v elan >/dev/null 2>&1 && [ ! -f "$HOME/.elan/bin/elan" ]; then
    if [[ -n "${ELAN_INSTALLER_URL:-}" ]]; then
        run_verified_shell_artifact "Elan" "${ELAN_INSTALLER_URL}" "${ELAN_INSTALLER_SHA256:-}" "${ELAN_ARTIFACT_VERSION:-}" -y --default-toolchain none \
            && ok "Elan instalado por artefato verificado." \
            || { err "Elan não foi instalado: artefato ausente ou inválido."; exit 1; }
    else
        warn "Elan não será baixado automaticamente. Forneça ELAN_INSTALLER_URL, ELAN_INSTALLER_SHA256 e ELAN_ARTIFACT_VERSION para habilitá-lo."
    fi
fi

# Integração nativa: o opencode.json do repositório carrega os agentes e o
# servidor MCP metacognitivo automaticamente quando o OpenCode CLI é aberto
# dentro da pasta do ecossistema. Regenera para garantir paths corretos:
if [ -f "$ECO_DIR/integrations/opencode_cli.py" ]; then
    (cd -- "$ECO_DIR" && "$VENV_PYTHON" -c "
from integrations.opencode_cli import OpenCodeCLIIntegration
integ = OpenCodeCLIIntegration('.')
path = integ.generate_config()
print(f'opencode.json regenerado: {path}')
" >>"$LOG_FILE" 2>&1) || { err "Não foi possível regenerar opencode.json."; exit 1; }
    ok "Integração nativa OpenCode CLI configurada."
fi

# Compilação e auditoria Microsoft APM (222 primitivas)
if [ -d "$ECO_DIR" ]; then
    log "Auditando e compilando pacotes Microsoft APM..."
    (cd -- "$ECO_DIR" && "$VENV_PYTHON" -m marceloclaro.cli apm compile >>"$LOG_FILE" 2>&1) \
        || { err "Falha ao compilar Microsoft APM (verifique o log)."; exit 1; }
    ok "Microsoft APM sincronizado com sucesso."
fi

# ---------------------------------------------------------------------------
# Smoke tests & Diagnóstico Doctor
# ---------------------------------------------------------------------------
echo ""
echo "==================================================================="
echo "  VERIFICAÇÃO FINAL & DIAGNÓSTICO DO ECOSSISTEMA"
echo "==================================================================="
export PATH="$HOME/.opencode/bin:$HOME/.local/bin:$HOME/.elan/bin:$PATH"
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

# Execução do Doctor para checagem estrutural completa
if [ -d "$ECO_DIR" ]; then
    echo ""
    log "Executando Doctor de integridade estrutural (19 checks)..."
    if (cd -- "$ECO_DIR" && "$VENV_PYTHON" -m marceloclaro.cli doctor >>"$LOG_FILE" 2>&1); then
        ok "Doctor executado pela virtualenv."
    else
        err "Doctor falhou — verifique $LOG_FILE."
        FAIL=1
    fi
fi

if [ "$FAIL" -ne 0 ]; then
    err "Smoke tests falharam; integração e atalhos não serão criados."
    exit 1
fi

BASHRC="$HOME/.bashrc"
if ! validate_ecosystem_dir "$ECO_DIR"; then
    err "ECOSYSTEM_DIR recusado antes de gravar aliases ou launchers."
    exit 1
fi
add_line() { grep -qxF "$1" "$BASHRC" 2>/dev/null || printf '%s\n' "$1" >> "$BASHRC"; }
add_line 'export PATH="$HOME/.opencode/bin:$HOME/.local/bin:$HOME/.elan/bin:$PATH"' || { err "Falha ao atualizar $BASHRC."; exit 1; }
add_line "alias ecosystem='cd -- \"$ECO_DIR\" && \"$VENV_PYTHON\" -m marceloclaro.cli'" || { err "Falha ao criar alias ecosystem."; exit 1; }
add_line "alias eco-opencode='cd -- \"$ECO_DIR\" && opencode'" || { err "Falha ao criar alias eco-opencode."; exit 1; }
add_line "alias eco-agy='cd -- \"$ECO_DIR\" && agy'" || { err "Falha ao criar alias eco-agy."; exit 1; }
add_line "alias eco-claude='cd -- \"$ECO_DIR\" && claude'" || { err "Falha ao criar alias eco-claude."; exit 1; }

# Criação / sincronização de atalhos somente após todos os smoke tests.
if [ -d "$ECO_DIR" ]; then
    echo ""
    log "Criando atalhos na Área de Trabalho (OpenCode, Antigravity, Claude Code, Ecosystem)..."
    (cd -- "$ECO_DIR" && "$VENV_PYTHON" -m marceloclaro.cli shortcuts >>"$LOG_FILE" 2>&1) \
        || { err "Falha ao configurar atalhos; provisionamento não foi concluído."; exit 1; }
    ok "Atalhos na Área de Trabalho criados e verificados com sucesso."
fi

echo ""
ok "Provisionamento concluído com sucesso total!"
exit 0
