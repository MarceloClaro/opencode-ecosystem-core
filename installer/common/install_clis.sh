#!/usr/bin/env bash
# ============================================================================
# OpenCode Ecosystem Core — instalação verificada de CLIs externas
# ----------------------------------------------------------------------------
# Esta biblioteca é carregada pelos instaladores Linux, macOS e WSL. Por
# segurança, ela nunca interpreta conteúdo vindo diretamente da rede. Cada
# artefato automático precisa de URL HTTPS, versão explícita e SHA-256
# informado pelo operador; ausência ou divergência do hash encerra o caminho.
# ============================================================================

declare -f log >/dev/null 2>&1 || log() { echo "[ECOSYSTEM] $*"; }
declare -f ok >/dev/null 2>&1 || ok() { echo "[OK] $*"; }
declare -f warn >/dev/null 2>&1 || warn() { echo "[AVISO] $*"; }
declare -f err >/dev/null 2>&1 || err() { echo "[ERRO] $*"; }
: "${LOG_FILE:=/tmp/opencode-ecosystem-install-clis.log}"

artifact_cache_override_is_set() {
    [[ -n "${ECOSYSTEM_ARTIFACT_CACHE:-}" ]]
}

private_artifact_cache_dir() {
    local home_dir="${HOME:-}"
    [[ -n "$home_dir" && "$home_dir" == /* ]] || return 1
    while [[ "$home_dir" != "/" && "$home_dir" == */ ]]; do
        home_dir="${home_dir%/}"
    done
    [[ "$home_dir" != "/" ]] || return 1
    printf '%s\n' "$home_dir/.cache/opencode-ecosystem/artifacts"
}

artifact_cache_dir() {
    if artifact_cache_override_is_set; then
        err "ECOSYSTEM_ARTIFACT_CACHE não pode substituir a raiz privada de artefatos."
        return 1
    fi
    private_artifact_cache_dir || {
        err "HOME deve ser um caminho absoluto para o cache privado de artefatos."
        return 1
    }
}

artifact_cache_owner_uid() {
    local path="$1" owner
    if owner="$(stat -c '%u' "$path" 2>/dev/null)"; then
        printf '%s\n' "$owner"
        return 0
    fi
    owner="$(stat -f '%u' "$path" 2>/dev/null)" || return 1
    printf '%s\n' "$owner"
}

artifact_cache_mode() {
    local path="$1" mode
    if mode="$(stat -c '%a' "$path" 2>/dev/null)"; then
        printf '%s\n' "$mode"
        return 0
    fi
    mode="$(stat -f '%Lp' "$path" 2>/dev/null)" || return 1
    printf '%s\n' "$mode"
}

artifact_cache_mode_has_no_external_write() {
    local mode="$1"
    [[ "$mode" =~ ^[0-7]{3,4}$ ]] || return 1
    (( (8#$mode & 8#022) == 0 ))
}

ensure_private_artifact_cache() {
    # A árvore é construída internamente sob HOME e estado legado inseguro é
    # recusado; nunca seguimos links nem corrigimos permissões por pathname.
    local cache_root current component next current_uid home_owner owner mode home_dir="${HOME:-}"

    if artifact_cache_override_is_set; then
        err "ECOSYSTEM_ARTIFACT_CACHE é recusado; use a raiz privada fixa sob HOME."
        return 1
    fi
    cache_root="$(private_artifact_cache_dir)" || {
        err "HOME deve ser um caminho absoluto para o cache privado de artefatos."
        return 1
    }
    while [[ "$home_dir" != "/" && "$home_dir" == */ ]]; do
        home_dir="${home_dir%/}"
    done
    current_uid="$(id -u 2>/dev/null)" || {
        err "Não foi possível identificar o proprietário do cache privado."
        return 1
    }
    if [[ -L "$home_dir" || ! -d "$home_dir" ]]; then
        err "HOME deve apontar para um diretório real antes de criar o cache privado."
        return 1
    fi
    home_owner="$(artifact_cache_owner_uid "$home_dir")" || {
        err "Não foi possível verificar o proprietário de HOME."
        return 1
    }
    if [[ "$home_owner" != "$current_uid" ]]; then
        err "HOME deve pertencer ao usuário atual para criar o cache privado."
        return 1
    fi
    mode="$(artifact_cache_mode "$home_dir")" || {
        err "Não foi possível verificar as permissões de HOME."
        return 1
    }
    if ! artifact_cache_mode_has_no_external_write "$mode"; then
        err "HOME possui permissão de escrita externa e não é seguro para o cache privado."
        return 1
    fi
    # Diretórios novos nascem privados. A implementação não ajusta permissões
    # de componentes já existentes, inclusive quando pertencem ao usuário.
    umask 077
    current="$home_dir"
    for component in .cache opencode-ecosystem artifacts; do
        next="$current/$component"
        if [[ -L "$next" ]]; then
            err "Cache privado recusado: componente simbólico em $next."
            return 1
        fi
        if [[ -e "$next" ]]; then
            if [[ ! -d "$next" ]]; then
                err "Cache privado recusado: componente não é diretório em $next."
                return 1
            fi
        elif ! mkdir "$next"; then
            err "Não foi possível criar a raiz privada de artefatos."
            return 1
        fi
        if [[ -L "$next" || ! -d "$next" ]]; then
            err "Cache privado recusado após criação: $next."
            return 1
        fi
        owner="$(artifact_cache_owner_uid "$next")" || {
            err "Não foi possível verificar o proprietário do cache privado."
            return 1
        }
        if [[ "$owner" != "$current_uid" ]]; then
            err "Cache privado recusado: $next não pertence ao usuário atual."
            return 1
        fi
        mode="$(artifact_cache_mode "$next")" || {
            err "Não foi possível verificar as permissões do cache privado."
            return 1
        }
        if [[ "$component" == "artifacts" ]]; then
            if [[ "$mode" != "700" ]]; then
                err "A raiz privada de artefatos existente deve ter permissão 0700."
                return 1
            fi
        elif ! artifact_cache_mode_has_no_external_write "$mode"; then
            err "Cache privado recusado: componente gravável por terceiros em $next."
            return 1
        fi
        current="$next"
    done

    # Não corrigimos permissões de árvore existente por pathname: um estado
    # legado inseguro foi recusado no laço acima. Diretórios novos já nasceram
    # com umask 077 e a raiz foi confirmada como 0700.
    if [[ -L "$cache_root" || ! -d "$cache_root" ]]; then
        err "Cache privado recusado após validação de permissões."
        return 1
    fi
    owner="$(artifact_cache_owner_uid "$cache_root")" || return 1
    mode="$(artifact_cache_mode "$cache_root")" || return 1
    if [[ "$owner" != "$current_uid" || "$mode" != "700" ]]; then
        err "A raiz privada de artefatos não atende à propriedade e permissão exigidas."
        return 1
    fi
    return 0
}

ensure_private_artifact_cache_subdirectory() {
    # Componentes internos também não podem ser links; a raiz 0700 impede
    # escrita de terceiros, e esta checagem evita seguir estado legado inseguro.
    local relative_path="$1" cache_root current component remaining next current_uid owner

    [[ "$relative_path" =~ ^[A-Za-z0-9._-]+(/[A-Za-z0-9._-]+)*$ ]] || {
        err "Subdiretório de cache inválido."
        return 1
    }
    ensure_private_artifact_cache || return 1
    cache_root="$(artifact_cache_dir)" || return 1
    current_uid="$(id -u 2>/dev/null)" || return 1
    current="$cache_root"
    remaining="$relative_path"
    while [[ -n "$remaining" ]]; do
        component="${remaining%%/*}"
        if [[ "$remaining" == */* ]]; then
            remaining="${remaining#*/}"
        else
            remaining=""
        fi
        next="$current/$component"
        if [[ -L "$next" ]]; then
            err "Cache privado recusado: subdiretório simbólico em $next."
            return 1
        fi
        if [[ -e "$next" ]]; then
            [[ -d "$next" ]] || {
                err "Cache privado recusado: subdiretório não é diretório em $next."
                return 1
            }
        elif ! mkdir "$next"; then
            err "Não foi possível criar subdiretório do cache privado."
            return 1
        fi
        if [[ -L "$next" || ! -d "$next" ]]; then
            err "Cache privado recusado após criar subdiretório em $next."
            return 1
        fi
        owner="$(artifact_cache_owner_uid "$next")" || return 1
        if [[ "$owner" != "$current_uid" ]]; then
            err "Cache privado recusado: subdiretório não pertence ao usuário atual."
            return 1
        fi
        current="$next"
    done
    printf '%s\n' "$current"
}

sha256_file() {
    local path="$1"
    if command -v sha256sum >/dev/null 2>&1; then
        sha256sum "$path" | cut -d ' ' -f1
    elif command -v shasum >/dev/null 2>&1; then
        shasum -a 256 "$path" | cut -d ' ' -f1
    else
        err "Nenhuma ferramenta SHA-256 disponível (sha256sum ou shasum)."
        return 1
    fi
}

is_sha256() {
    [[ "$1" =~ ^[A-Fa-f0-9]{64}$ ]]
}

normalize_sha256() {
    printf '%s' "$1" | tr '[:upper:]' '[:lower:]'
}

is_immutable_version() {
    # O valor entra em nomes de cache e precisa ser uma versão, não um caminho.
    local version="$1" normalized
    [[ "$version" =~ ^[A-Za-z0-9][A-Za-z0-9._+-]{0,127}$ ]] || return 1
    normalized="$(printf '%s' "$version" | tr '[:upper:]' '[:lower:]')"
    [[ "$normalized" != "main" && "$normalized" != "latest" ]]
}

is_https_artifact_url() {
    local url="$1" version="$2" authority normalized_url

    [[ "$url" =~ ^https:// ]] || return 1
    [[ "$url" != *$'\n'* && "$url" != *$'\r'* && "$url" != *$'\t'* && "$url" != *' '* ]] || return 1
    [[ "$url" != *'?'* && "$url" != *'#'* ]] || return 1
    authority="${url#https://}"
    authority="${authority%%/*}"
    [[ -n "$authority" && "$authority" != *'@'* ]] || return 1
    normalized_url="$(printf '%s' "$url" | tr '[:upper:]' '[:lower:]')"
    [[ ! "$normalized_url" =~ (^|[/\?&=])(main|latest)([/\?&=]|$) ]] || return 1
    # A versão explícita também precisa fazer parte da localização do artefato.
    [[ "$url" == *"$version"* ]]
}

validate_https_artifact_provenance() {
    # Esta validação é pura: não cria cache, não abre rede e não executa CLI.
    local label="$1" url="$2" expected_sha="$3" version="$4"

    if ! is_immutable_version "$version"; then
        err "$label requer versão explícita e imutável."
        return 1
    fi
    if ! is_https_artifact_url "$url" "$version"; then
        err "$label requer URL HTTPS versionada, sem credenciais, consultas, fragmentos ou referências móveis."
        return 1
    fi
    if ! is_sha256 "$expected_sha"; then
        err "$label requer SHA-256 de 64 dígitos fornecido pelo operador."
        return 1
    fi
}

validate_npm_artifact_provenance() {
    # A procedência do tarball NPM também precisa estar completa antes de npm.
    local label="$1" version="$2" expected_sha="$3"

    if ! is_immutable_version "$version"; then
        err "$label requer versão NPM explícita e imutável."
        return 1
    fi
    if ! is_sha256 "$expected_sha"; then
        err "$label requer SHA-256 do tarball NPM principal."
        return 1
    fi
}

preflight_external_artifacts() {
    # Valida somente a configuração selecionada antes de sudo, apt, brew, npm,
    # curl, cache ou qualquer instalação. Ausência é falha fechada, não fallback.
    if [[ -n "${OPENCODE_INSTALLER_URL:-}" ]]; then
        validate_https_artifact_provenance \
            "OpenCode CLI" \
            "${OPENCODE_INSTALLER_URL}" \
            "${OPENCODE_INSTALLER_SHA256:-}" \
            "${OPENCODE_ARTIFACT_VERSION:-}" || return 1
    else
        if [[ -n "${OPENCODE_INSTALLER_SHA256:-}" || -n "${OPENCODE_ARTIFACT_VERSION:-}" ]]; then
            err "Metadados do instalador OpenCode exigem OPENCODE_INSTALLER_URL."
            return 1
        fi
        validate_npm_artifact_provenance \
            "OpenCode CLI" \
            "${OPENCODE_NPM_VERSION:-}" \
            "${OPENCODE_NPM_SHA256:-}" || return 1
    fi

    validate_https_artifact_provenance \
        "Antigravity CLI" \
        "${ANTIGRAVITY_INSTALLER_URL:-}" \
        "${ANTIGRAVITY_INSTALLER_SHA256:-}" \
        "${ANTIGRAVITY_ARTIFACT_VERSION:-}" || return 1
    validate_npm_artifact_provenance \
        "Claude Code CLI" \
        "${CLAUDE_CODE_VERSION:-}" \
        "${CLAUDE_CODE_NPM_SHA256:-}" || return 1
    validate_https_artifact_provenance \
        "Ollama" \
        "${OLLAMA_BINARY_URL:-}" \
        "${OLLAMA_BINARY_SHA256:-}" \
        "${OLLAMA_ARTIFACT_VERSION:-}" || return 1

    # Elan é opcional no provisionador WSL, mas uma configuração parcial não
    # pode chegar ao download tardio depois das etapas privilegiadas.
    if [[ -n "${ELAN_INSTALLER_URL:-}" || -n "${ELAN_INSTALLER_SHA256:-}" || -n "${ELAN_ARTIFACT_VERSION:-}" ]]; then
        validate_https_artifact_provenance \
            "Elan" \
            "${ELAN_INSTALLER_URL:-}" \
            "${ELAN_INSTALLER_SHA256:-}" \
            "${ELAN_ARTIFACT_VERSION:-}" || return 1
    fi
}

artifact_cache_path() {
    # O hash faz parte da chave para impedir a reutilização de cache de outra
    # declaração de procedência para a mesma versão.
    local label="$1" version="$2" expected_sha="$3" safe_label normalized_sha cache_root
    safe_label="$(printf '%s' "$label" | tr -cs '[:alnum:]._- ' '_')"
    normalized_sha="$(normalize_sha256 "$expected_sha")"
    cache_root="$(artifact_cache_dir)" || return 1
    printf '%s/cache/%s-%s-%s.artifact\n' "$cache_root" "$safe_label" "$version" "$normalized_sha"
}

hash_matches() {
    local path="$1" expected_sha="$2" actual_sha
    actual_sha="$(sha256_file "$path")" || return 1
    [[ "$(normalize_sha256 "$actual_sha")" == "$(normalize_sha256 "$expected_sha")" ]]
}

verify_cached_artifact() {
    # Cache nunca é uma fonte de confiança: é rehashado a cada reutilização.
    local label="$1" path="$2" expected_sha="$3"
    [[ -f "$path" && ! -L "$path" ]] || return 1
    if hash_matches "$path" "$expected_sha"; then
        return 0
    fi
    rm -f "$path"
    warn "Cache inválido descartado para $label."
    return 1
}

require_verified_https_artifact() {
    # Uso: label url sha256 version destination
    local label="$1" url="$2" expected_sha="$3" version="$4" destination="$5"
    local cache_path cache_directory temporary destination_temporary

    if ! ensure_private_artifact_cache; then
        return 1
    fi
    if ! is_immutable_version "$version"; then
        err "$label requer ARTIFACT_VERSION explícita e imutável; 'main' e 'latest' são recusados."
        return 1
    fi
    if ! is_https_artifact_url "$url" "$version"; then
        err "$label requer URL HTTPS versionada, sem credenciais, fragmentos ou referências móveis."
        return 1
    fi
    if ! is_sha256 "$expected_sha"; then
        err "$label requer SHA-256 de 64 dígitos fornecido pelo operador."
        return 1
    fi
    if ! command -v curl >/dev/null 2>&1; then
        err "curl é necessário para baixar $label."
        return 1
    fi
    if [[ -d "$destination" ]]; then
        err "Destino de $label é um diretório, não um arquivo."
        return 1
    fi

    cache_directory="$(ensure_private_artifact_cache_subdirectory cache)" || return 1
    cache_path="$(artifact_cache_path "$label" "$version" "$expected_sha")" || return 1
    [[ "$(dirname "$cache_path")" == "$cache_directory" ]] || return 1
    mkdir -p "$(dirname "$destination")" || return 1

    if verify_cached_artifact "$label" "$cache_path" "$expected_sha"; then
        ok "$label $version recuperado de cache revalidado por SHA-256."
    else
        temporary="$(mktemp "${cache_path}.tmp.XXXXXX")" || return 1
        if ! curl --fail --location --max-redirs 3 --proto '=https' --proto-redir '=https' --tlsv1.2 --retry 3 --output "$temporary" "$url" >>"$LOG_FILE" 2>&1; then
            rm -f "$temporary"
            err "Falha ao baixar $label por HTTPS."
            return 1
        fi
        if ! hash_matches "$temporary" "$expected_sha"; then
            rm -f "$temporary"
            err "SHA-256 inválido para $label; artefato descartado."
            return 1
        fi
        chmod 0600 "$temporary" || { rm -f "$temporary"; return 1; }
        mv -f "$temporary" "$cache_path" || { rm -f "$temporary"; return 1; }
        ok "$label $version baixado e verificado por SHA-256."
    fi

    # A cópia final é rehashada antes do consumo, inclusive quando veio do
    # cache local. Operações por pathname em shell não eliminam uma janela
    # TOCTOU contra uma escrita local concorrente entre essa checagem e o uso.
    destination_temporary="$(mktemp "${destination}.tmp.XXXXXX")" || return 1
    if ! cp "$cache_path" "$destination_temporary" || ! hash_matches "$destination_temporary" "$expected_sha"; then
        rm -f "$destination_temporary"
        err "Não foi possível preparar bytes verificados para $label."
        return 1
    fi
    chmod 0700 "$destination_temporary" || { rm -f "$destination_temporary"; return 1; }
    mv -f "$destination_temporary" "$destination" || { rm -f "$destination_temporary"; return 1; }
    ok "$label $version verificado por SHA-256."
}

run_verified_shell_artifact() {
    # Uso: label url sha256 version [argumentos do instalador...]
    local label="$1" url="$2" expected_sha="$3" version="$4"
    shift 4
    local safe_label artifact artifact_directory normalized_sha
    ensure_private_artifact_cache || return 1
    safe_label="$(printf '%s' "$label" | tr -cs '[:alnum:]._- ' '_')"
    normalized_sha="$(normalize_sha256 "$expected_sha")"
    artifact_directory="$(ensure_private_artifact_cache_subdirectory executables)" || return 1
    artifact="$artifact_directory/${safe_label}-${version}-${normalized_sha}.sh"

    require_verified_https_artifact "$label" "$url" "$expected_sha" "$version" "$artifact" || return 1
    /bin/bash "$artifact" "$@" >>"$LOG_FILE" 2>&1
}

installer_system_path() {
    # Não herda PATH de chamadores: antes de baixar/verificar artefatos, apenas
    # diretórios de sistema podem resolver ferramentas auxiliares.
    printf '%s\n' '/opt/homebrew/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
}

system_executable() {
    local name="$1" candidate

    [[ "$name" =~ ^[a-z][a-z0-9_-]*$ ]] || return 1
    for candidate in "/usr/bin/$name" "/bin/$name"; do
        if [[ -x "$candidate" ]]; then
            printf '%s\n' "$candidate"
            return 0
        fi
    done
    return 1
}

install_verified_npm_package() {
    # Uso: package version sha256. O tarball é validado antes de npm install.
    local package="$1" version="$2" expected_sha="$3"
    local safe_package cache_dir tarball npm_registry normalized_sha nullglob_was_set
    local tarballs=()

    ensure_private_artifact_cache || return 1
    if ! is_immutable_version "$version"; then
        err "$package requer versão NPM explícita; 'latest' é recusado."
        return 1
    fi
    if ! is_sha256 "$expected_sha"; then
        err "$package requer SHA-256 do tarball NPM."
        return 1
    fi
    if ! command -v npm >/dev/null 2>&1; then
        err "npm não disponível para instalar $package."
        return 1
    fi
    npm_registry="$(npm config get registry 2>>"$LOG_FILE")"
    if ! is_https_artifact_url "$npm_registry" ""; then
        err "O registry NPM deve usar HTTPS; registry atual recusado."
        return 1
    fi

    safe_package="$(printf '%s' "$package" | tr '/@' '__')"
    normalized_sha="$(normalize_sha256 "$expected_sha")"
    cache_dir="$(ensure_private_artifact_cache_subdirectory "npm/${safe_package}-${version}-${normalized_sha}")" || return 1
    shopt -q nullglob && nullglob_was_set=1 || nullglob_was_set=0
    shopt -s nullglob
    tarballs=("$cache_dir"/*.tgz)
    if [[ "$nullglob_was_set" -eq 0 ]]; then shopt -u nullglob; fi
    if [[ "${#tarballs[@]}" -eq 1 ]] && verify_cached_artifact "$package" "${tarballs[0]}" "$expected_sha"; then
        tarball="${tarballs[0]}"
        ok "Tarball NPM $package@$version recuperado de cache revalidado."
    else
        rm -f "$cache_dir"/*.tgz
        if ! npm pack "${package}@${version}" --ignore-scripts --pack-destination "$cache_dir" --registry "$npm_registry" >>"$LOG_FILE" 2>&1; then
            err "Falha ao obter o tarball versionado de $package."
            return 1
        fi
        shopt -s nullglob
        tarballs=("$cache_dir"/*.tgz)
        if [[ "$nullglob_was_set" -eq 0 ]]; then shopt -u nullglob; fi
        if [[ "${#tarballs[@]}" -ne 1 ]] || ! verify_cached_artifact "$package" "${tarballs[0]}" "$expected_sha"; then
            err "SHA-256 inválido ou tarball ambíguo para $package; instalação bloqueada."
            return 1
        fi
        tarball="${tarballs[0]}"
    fi
    # O hash declarado autentica somente o tarball principal. O --offline evita
    # download nesta etapa, mas o NPM pode consumir dependências transitivas já
    # presentes no cache local. Este script não verifica individualmente a
    # procedência ou os hashes transitivos desse cache; se faltar algo, a
    # instalação falha em vez de buscar bytes adicionais sem declaração.
    npm install --global --prefix "$HOME/.local" --ignore-scripts --offline "$tarball" >>"$LOG_FILE" 2>&1 || {
        err "Falha ao instalar $package em modo offline; o cache NPM pode não conter dependências transitivas (não verificadas individualmente por este script)."
        return 1
    }
}

install_opencode_cli() {
    log "Instalando OpenCode CLI com artefato verificado..."
    if command -v opencode >/dev/null 2>&1; then
        ok "OpenCode CLI já está disponível; o binário existente não foi executado."
        return 0
    fi
    if [[ -n "${OPENCODE_INSTALLER_URL:-}" ]]; then
        run_verified_shell_artifact "OpenCode CLI" "${OPENCODE_INSTALLER_URL}" "${OPENCODE_INSTALLER_SHA256:-}" "${OPENCODE_ARTIFACT_VERSION:-}" || return 1
    else
        install_verified_npm_package "opencode-ai" "${OPENCODE_NPM_VERSION:-}" "${OPENCODE_NPM_SHA256:-}" || return 1
    fi
    export PATH="$HOME/.opencode/bin:$HOME/.local/bin:$PATH"
    command -v opencode >/dev/null 2>&1 || { err "OpenCode não apareceu no PATH após instalação verificada."; return 1; }
    ok "OpenCode CLI instalado por artefato verificado."
}

install_antigravity_cli() {
    log "Instalando Antigravity CLI com artefato verificado..."
    if command -v agy >/dev/null 2>&1 || [[ -x "$HOME/.local/bin/agy" ]]; then
        ok "Antigravity CLI já instalado."
        return 0
    fi
    run_verified_shell_artifact "Antigravity CLI" "${ANTIGRAVITY_INSTALLER_URL:-}" "${ANTIGRAVITY_INSTALLER_SHA256:-}" "${ANTIGRAVITY_ARTIFACT_VERSION:-}" || return 1
    export PATH="$HOME/.local/bin:$PATH"
    command -v agy >/dev/null 2>&1 || { err "Antigravity CLI não apareceu no PATH após instalação verificada."; return 1; }
    ok "Antigravity CLI instalado por artefato verificado."
}

install_claude_code_cli() {
    log "Instalando Claude Code CLI com tarball NPM verificado..."
    if command -v claude >/dev/null 2>&1; then
        ok "Claude Code CLI já está disponível; o binário existente não foi executado."
        return 0
    fi
    install_verified_npm_package "@anthropic-ai/claude-code" "${CLAUDE_CODE_VERSION:-}" "${CLAUDE_CODE_NPM_SHA256:-}" || return 1
    export PATH="$HOME/.local/bin:$PATH"
    command -v claude >/dev/null 2>&1 || { err "Claude Code não apareceu no PATH após instalação verificada."; return 1; }
    ok "Claude Code CLI instalado por tarball verificado."
}

install_ollama_cli() {
    local ollama_bin="$HOME/.local/bin/ollama" nohup_bin="" pgrep_bin="" sleep_bin=""

    log "Preparando Ollama exclusivamente por binário verificado..."
    # Um binário já presente pode existir fora da procedência declarada. Nunca
    # o executamos nem acionamos uma unidade systemd desconhecida com privilégio.
    require_verified_https_artifact "Ollama" "${OLLAMA_BINARY_URL:-}" "${OLLAMA_BINARY_SHA256:-}" "${OLLAMA_ARTIFACT_VERSION:-}" "$ollama_bin" || return 1
    [[ -x "$ollama_bin" && ! -L "$ollama_bin" ]] || {
        err "O binário Ollama verificado não está executável no destino privado."
        return 1
    }
    if pgrep_bin="$(system_executable pgrep)" && "$pgrep_bin" -f "ollama serve" >/dev/null 2>&1; then
        ok "Ollama já possui processo em execução; nenhum binário pré-existente foi iniciado."
        return 0
    fi
    nohup_bin="$(system_executable nohup)" || {
        err "nohup do sistema não foi encontrado para iniciar o binário Ollama verificado."
        return 1
    }
    sleep_bin="$(system_executable sleep)" || {
        err "sleep do sistema não foi encontrado para confirmar a inicialização do Ollama."
        return 1
    }
    "$nohup_bin" "$ollama_bin" serve >>"$LOG_FILE" 2>&1 &
    "$sleep_bin" 2
    ok "Ollama iniciado por binário verificado no diretório privado do usuário."
}

install_all_clis() {
    local safe_system_path

    safe_system_path="$(installer_system_path)" || return 1
    preflight_external_artifacts || return 1
    ( PATH="$safe_system_path"; export PATH; install_opencode_cli ) || return 1
    ( PATH="$safe_system_path"; export PATH; install_antigravity_cli ) || return 1
    ( PATH="$safe_system_path"; export PATH; install_claude_code_cli ) || return 1
    ( PATH="$safe_system_path"; export PATH; install_ollama_cli ) || return 1
}
