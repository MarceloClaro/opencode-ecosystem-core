#!/usr/bin/env bash
# ==========================================================================
# OpenCode Ecosystem Core — validação de caminhos persistidos por instalador
# --------------------------------------------------------------------------
# Esta biblioteca é carregada antes de gravar aliases ou launchers. Ela aceita
# apenas um diretório absoluto, estritamente abaixo de HOME, com componentes
# ASCII previsíveis para que o valor nunca precise ser reinterpretado por um
# shell ou formato de launcher.
# ==========================================================================

path_safety_error() {
    if declare -F err >/dev/null 2>&1; then
        err "$1"
    else
        printf '%s\n' "[ERRO] $1" >&2
    fi
}

validate_ecosystem_dir() {
    # Uso: validate_ecosystem_dir /caminho/absoluto/sob/home
    # O diretório pode ainda não existir, portanto a contenção é lexical e os
    # segmentos de normalização são recusados em vez de resolvidos.
    local ecosystem_dir="${1-}" home_dir="${HOME-}"

    if [[ -z "$home_dir" || -z "$ecosystem_dir" ]]; then
        path_safety_error "ECOSYSTEM_DIR e HOME devem estar definidos."
        return 1
    fi
    if [[ "$home_dir" != /* || "$ecosystem_dir" != /* ]]; then
        path_safety_error "ECOSYSTEM_DIR deve ser um caminho absoluto sob HOME."
        return 1
    fi

    # Um HOME com barra final é normalizado somente para a comparação de
    # fronteira. A raiz do sistema não é uma base aceitável para persistência.
    while [[ "$home_dir" != "/" && "$home_dir" == */ ]]; do
        home_dir="${home_dir%/}"
    done
    if [[ "$home_dir" == "/" ]]; then
        path_safety_error "HOME não pode ser a raiz do sistema para ECOSYSTEM_DIR."
        return 1
    fi

    # Espaços, Unicode e metacaracteres de shell/launcher ficam fora do
    # contrato deliberadamente. Pontos são aceitos apenas em nomes, não como
    # segmentos de normalização.
    if [[ ! "$home_dir" =~ ^/[A-Za-z0-9._/-]+$ ]] || [[ ! "$ecosystem_dir" =~ ^/[A-Za-z0-9._/-]+$ ]]; then
        path_safety_error "ECOSYSTEM_DIR contém caracteres não permitidos para persistência."
        return 1
    fi
    if [[ "$home_dir" == *"//"* || "$ecosystem_dir" == *"//"* ]] || \
       [[ "/$home_dir/" == *"/./"* || "/$home_dir/" == *"/../"* ]] || \
       [[ "/$ecosystem_dir/" == *"/./"* || "/$ecosystem_dir/" == *"/../"* ]]; then
        path_safety_error "ECOSYSTEM_DIR não pode conter segmentos ambíguos."
        return 1
    fi

    case "$ecosystem_dir" in
        "$home_dir"/*) return 0 ;;
        *)
            path_safety_error "ECOSYSTEM_DIR deve permanecer estritamente sob HOME."
            return 1
            ;;
    esac
}

validate_ecosystem_dir_no_symlink_prefix() {
    # Uso: validate_ecosystem_dir_no_symlink_prefix /caminho/a/criar
    # Antes de git clone, todo componente que já existe entre HOME e o destino
    # precisa ser um diretório real. Isso impede que um pai simbólico redirecione
    # a primeira escrita para fora da fronteira lexical validada.
    local ecosystem_dir="${1-}" home_dir="${HOME-}" relative_path current component

    validate_ecosystem_dir "$ecosystem_dir" || return 1
    while [[ "$home_dir" != "/" && "$home_dir" == */ ]]; do
        home_dir="${home_dir%/}"
    done
    if [[ ! -d "$home_dir" || -L "$home_dir" ]]; then
        path_safety_error "HOME deve ser um diretório real antes da instalação."
        return 1
    fi

    relative_path="${ecosystem_dir#"$home_dir"/}"
    current="$home_dir"
    IFS='/' read -r -a components <<< "$relative_path"
    for component in "${components[@]}"; do
        [[ -n "$component" ]] || {
            path_safety_error "ECOSYSTEM_DIR contém componente vazio."
            return 1
        }
        current="$current/$component"
        if [[ -L "$current" ]]; then
            path_safety_error "ECOSYSTEM_DIR possui componente simbólico: $current."
            return 1
        fi
        if [[ -e "$current" && ! -d "$current" ]]; then
            path_safety_error "ECOSYSTEM_DIR possui componente que não é diretório: $current."
            return 1
        fi
    done
}

canonicalize_ecosystem_dir() {
    # Uso: canonicalize_ecosystem_dir /caminho/já-existente
    # A validação lexical ocorre antes do cd; depois, o alvo físico é validado
    # novamente para que um link simbólico sob HOME não persista um diretório
    # localizado fora da raiz permitida.
    local ecosystem_dir="${1-}" canonical_dir

    validate_ecosystem_dir_no_symlink_prefix "$ecosystem_dir" || return 1
    if [[ ! -d "$ecosystem_dir" ]]; then
        path_safety_error "ECOSYSTEM_DIR deve existir antes da canonicalização."
        return 1
    fi
    canonical_dir="$(CDPATH= cd -- "$ecosystem_dir" && pwd -P)" || {
        path_safety_error "Não foi possível canonicalizar ECOSYSTEM_DIR."
        return 1
    }
    validate_ecosystem_dir "$canonical_dir" || {
        path_safety_error "ECOSYSTEM_DIR canônico saiu de HOME e foi recusado."
        return 1
    }
    printf '%s\n' "$canonical_dir"
}
