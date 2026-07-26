#!/usr/bin/env bash
# LiteRT-LM lifecycle compatibility wrapper — SPEC-935-R212.
# A fonte de verdade é integrations.litert_lm_supervisor; este arquivo não
# executa check→spawn próprio e, portanto, não pode duplicar o daemon.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
SUPERVISOR=("$PYTHON_BIN" -m integrations.litert_lm_supervisor)

run_supervisor() {
    PYTHONPATH="$PROJECT_DIR${PYTHONPATH:+:$PYTHONPATH}" \
        "${SUPERVISOR[@]}" "$@"
}

case "${1:-ensure}" in
    --status|status)
        exec env PYTHONPATH="$PROJECT_DIR${PYTHONPATH:+:$PYTHONPATH}" \
            "${SUPERVISOR[@]}" status --json
        ;;
    --stop|stop)
        exec env PYTHONPATH="$PROJECT_DIR${PYTHONPATH:+:$PYTHONPATH}" \
            "${SUPERVISOR[@]}" stop --json
        ;;
    --restart|restart)
        run_supervisor stop --json
        exec env PYTHONPATH="$PROJECT_DIR${PYTHONPATH:+:$PYTHONPATH}" \
            "${SUPERVISOR[@]}" ensure --json
        ;;
    --non-blocking)
        exec env PYTHONPATH="$PROJECT_DIR${PYTHONPATH:+:$PYTHONPATH}" \
            "${SUPERVISOR[@]}" ensure --non-blocking --json
        ;;
    --log|log)
        if systemctl --user cat litert-lm.service >/dev/null 2>&1; then
            exec journalctl --user -u litert-lm.service -n 50 --no-pager
        fi
        echo "Unit litert-lm.service não instalada; consulte o journal/processo supervisor." >&2
        exit 1
        ;;
    ensure|start|"")
        exec env PYTHONPATH="$PROJECT_DIR${PYTHONPATH:+:$PYTHONPATH}" \
            "${SUPERVISOR[@]}" ensure --json
        ;;
    -h|--help)
        printf '%s\n' \
            "Uso: $0 [ensure|--non-blocking|--status|--stop|--restart|--log]"
        ;;
    *)
        echo "Opção desconhecida: $1" >&2
        exit 2
        ;;
esac
